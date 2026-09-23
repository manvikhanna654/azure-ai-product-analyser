"""Microsoft Foundry service for product image analysis and Q&A."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ANALYSIS_INSTRUCTIONS = """You are an AI Product Visualizer.

Analyze the uploaded product image and return only information that can be
reasonably determined from the image. Do not invent specifications, model
numbers, dimensions, performance claims, brand details, or hidden information.
Clearly distinguish visible facts from uncertain inferences.

Return the requested JSON fields. Use concise strings and arrays of strings.
For product identity, extract the brand, product name, model number, variant,
and visible specifications. If a model number is not readable or visible,
return an empty model_number rather than guessing.
For information that cannot be determined, use an empty array or a short
explanation in the cannot_determine field.
"""

ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overview": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "Category": {"type": "string"},
                "Product Type": {"type": "string"},
                "Primary Color": {"type": "string"},
                "Material": {"type": "string"},
                "Style": {"type": "string"},
            },
            "required": ["Category", "Product Type", "Primary Color", "Material", "Style"],
        },
        "identity": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "brand": {"type": "string"},
                "product_name": {"type": "string"},
                "model_number": {"type": "string"},
                "variant": {"type": "string"},
                "specifications": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["brand", "product_name", "model_number", "variant", "specifications"],
        },
        "attributes": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "Colors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {"name": {"type": "string"}, "hex": {"type": "string"}},
                        "required": ["name", "hex"],
                    },
                },
                "Material": {"type": "array", "items": {"type": "string"}},
                "Shape": {"type": "array", "items": {"type": "string"}},
                "Style": {"type": "array", "items": {"type": "string"}},
                "Features": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["Colors", "Material", "Shape", "Style", "Features"],
        },
        "description": {"type": "string"},
        "confidence": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"label": {"type": "string"}, "score": {"type": "integer", "minimum": 0, "maximum": 100}},
            "required": ["label", "score"],
        },
        "confidently_identified": {"type": "array", "items": {"type": "string"}},
        "cannot_determine": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["overview", "identity", "attributes", "description", "confidence", "confidently_identified", "cannot_determine"],
}


def _setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("PASTE_"):
        raise RuntimeError(f"{name} is missing from your .env file.")
    return value


def _client() -> tuple[OpenAI, str]:
    endpoint = _setting("FOUNDRY_PROJECT_ENDPOINT").rstrip("/")
    if not endpoint.endswith("/openai/v1"):
        endpoint = f"{endpoint}/openai/v1"
    return OpenAI(base_url=f"{endpoint}/", api_key=_setting("FOUNDRY_API_KEY")), _setting("FOUNDRY_MODEL")


def _data_url(image_bytes: bytes, mime_type: str | None) -> str:
    detected_type = mime_type or mimetypes.guess_type("product-image")[0]
    if detected_type not in {"image/jpeg", "image/png", "image/webp"}:
        detected_type = "image/jpeg"
    return f"data:{detected_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"


def _response_text(response: Any) -> str:
    text = getattr(response, "output_text", "")
    if not text:
        raise RuntimeError("Foundry returned an empty response.")
    return text


def analyze_product(image_bytes: bytes, mime_type: str | None) -> dict[str, Any]:
    """Analyze a product image and return the UI's analysis contract."""
    client, model = _client()
    response = client.responses.create(
        model=model,
        instructions=ANALYSIS_INSTRUCTIONS,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": "Analyze this product image using the required JSON format."},
            {"type": "input_image", "image_url": _data_url(image_bytes, mime_type)},
        ]}],
        text={"format": {"type": "json_schema", "name": "product_analysis", "strict": True, "schema": ANALYSIS_SCHEMA}},
    )
    try:
        return json.loads(_response_text(response))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Foundry returned invalid analysis JSON.") from exc


def answer_product_question(image_bytes: bytes, mime_type: str | None, question: str) -> str:
    """Answer a question about the uploaded product image."""
    client, model = _client()
    response = client.responses.create(
        model=model,
        instructions=(
            "You are a product-visualization assistant. Answer only questions about "
            "the uploaded product, its visible appearance, attributes, specifications "
            "that can be seen, price, availability, care, or comparison with similar "
            "products. Do not answer general programming, homework, politics, news, "
            "or unrelated questions. If a question is unrelated, reply exactly: "
            "I can only answer questions about the uploaded product. "
            "Use visible evidence only. If the image does not provide enough evidence, "
            "say that clearly. Do not invent specifications or hidden product information."
        ),
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": question},
            {"type": "input_image", "image_url": _data_url(image_bytes, mime_type)},
        ]}],
    )
    return _response_text(response)


def search_product_prices(
    product_identity: dict[str, Any], location: str, exact_match: bool = False
) -> str:
    """Search current prices, clearly separating exact and comparable matches."""
    client, model = _client()
    brand = product_identity.get("brand", "")
    product_name = product_identity.get("product_name", "")
    model_number = product_identity.get("model_number", "")
    variant = product_identity.get("variant", "")
    specifications = ", ".join(product_identity.get("specifications", []))
    exact_identity = " | ".join(value for value in (brand, product_name, model_number, variant, specifications) if value)
    match_instruction = (
        "Only include listings with the same brand, model number, and variant. "
        "Label every result as an exact match."
        if exact_match
        else
        "The model number is not verified. Search for likely comparable products, "
        "but label every result 'Not an exact match' and never present it as the same product."
    )
    prompt = f"""Use web search to compare current prices for this product.

Exact product identity: {exact_identity}
Market/location: {location}

{match_instruction}
Search Amazon and Flipkart separately, then compare the product identity carefully.

Return a concise comparison. For each result include retailer, exact listing
name, price, currency, condition, availability, match confidence, date checked,
and a direct source URL. Prefer manufacturers and reputable retailers.
Never invent prices. Mention when shipping, tax, or location may change the
final price.
"""
    response = client.responses.create(
        model=model,
        tools=[{"type": "web_search"}],
        # Let Foundry select the hosted search tool when the prompt requires
        # current market data. This is the supported Responses API pattern
        # and avoids rejecting deployments that do not accept a forced tool
        # choice for web search.
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        input=prompt,
    )
    return _response_text(response)


def answer_web_question(
    product_name: str,
    question: str,
    location: str = "",
    product_identity: dict[str, Any] | None = None,
) -> str:
    """Answer a current-information question with web search and citations."""
    client, model = _client()
    location_hint = f" Market/location: {location}." if location else ""
    identity = product_identity or {"product_name": product_name}
    identity_text = " | ".join(
        value for value in (
            identity.get("brand", ""),
            identity.get("product_name", product_name),
            identity.get("model_number", ""),
            identity.get("variant", ""),
        ) if value
    )
    response = client.responses.create(
        model=model,
        tools=[{"type": "web_search"}],
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        input=(
            f"You must use web search, not the image alone, to answer this question about {identity_text}.{location_hint}\n\n"
            f"Question: {question}\n\n"
            "Use current reliable sources to answer only questions about the identified "
            "product, its price, availability, retailers, or comparable products. If the "
            "question is unrelated, reply exactly: I can only answer questions about the "
            "uploaded product. Include citations or direct URLs, and clearly label "
            "information that may change. Never invent prices or availability."
        ),
    )
    return _response_text(response)
