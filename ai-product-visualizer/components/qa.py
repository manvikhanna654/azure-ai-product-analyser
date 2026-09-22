"""Chat-style question panel attached to the current analysis."""

import html
import re

import streamlit as st

from components import theme
from data.mock_data import SUGGESTED_QUESTIONS
from services.ai_service import answer_product_question, answer_web_question

WEB_SEARCH_TERMS = (
    "price", "cost", "buy", "purchase", "cheapest", "compare", "comparison",
    "similar", "alternative", "available", "where can", "retailer",
)

PRODUCT_TERMS = (
    "product", "image", "photo", "item", "object",
    "brand", "model", "material", "color", "colour",
    "feature", "features", "design", "style", "shape",
    "size", "weight", "heavy", "light", "quality", "appearance", "look",
    "silver", "black", "white", "red", "blue", "green", "grey", "gray", "gold",
    "brown", "beige", "pink", "purple", "orange", "yellow",
    "display", "screen", "camera", "keyboard", "processor", "cpu", "ram",
    "memory", "storage", "ssd", "battery", "port", "usb",
    "specification", "specifications", "specs", "model number", "sku", "serial",
    "price", "cost", "buy", "purchase", "cheapest", "compare", "comparison",
    "similar", "alternative", "available", "availability", "website", "retailer",
    "seller", "stock", "shipping", "warranty", "care", "use", "usage",
    "compatible", "compatibility",
)

PRODUCT_CONTEXT_PHRASES = (
    "this product", "this item", "this laptop", "this phone", "this camera",
    "this device", "this image", "the product", "the item", "the laptop",
    "the phone", "the device", "about this", "what is this", "what does this",
)

UNRELATED_TERMS = (
    "python", "javascript", "java code", "programming", "code", "algorithm",
    "homework", "politics", "football", "cricket", "recipe", "song lyrics",
    "write an essay", "math problem",
)

REFUSAL = "I can only answer questions about the uploaded product."


def _contains_term(text: str, terms: tuple[str, ...]) -> bool:
    """Match whole words so short terms do not match inside other words."""
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms)


def _is_product_question(question: str) -> bool:
    """Keep Q&A focused on the uploaded product."""
    lowered = question.lower().strip()
    if _contains_term(lowered, UNRELATED_TERMS):
        return False
    if any(phrase in lowered for phrase in PRODUCT_CONTEXT_PHRASES):
        return True
    return _contains_term(lowered, PRODUCT_TERMS)


def _submit(question: str) -> None:
    question = question.strip()
    if not question:
        return
    st.session_state.qa.append({"role": "user", "text": question})
    if not _is_product_question(question):
        st.session_state.qa.append({"role": "ai", "text": REFUSAL, "source": "product_filter"})
        return
    used_web_search = False
    try:
        product_name = st.session_state.analysis["overview"].get("Product Type", "the product")
        if any(term in question.lower() for term in WEB_SEARCH_TERMS):
            identity = st.session_state.analysis.get("identity", {})
            answer = answer_web_question(product_name, question, product_identity=identity)
            used_web_search = True
        else:
            answer = answer_product_question(st.session_state.upload_bytes, st.session_state.upload_mime, question)
    except Exception as exc:
        answer = f"I could not answer that question: {exc}"
    st.session_state.qa.append({"role": "ai", "text": answer, "source": "web" if used_web_search else "image"})


def render_qa() -> None:
    theme.section(
        "Ask about this product",
        "Questions stay tied to the image you analysed.",
    )

    if not st.session_state.qa:
        st.markdown(
            '<div class="pv-card"><p>No questions yet. Pick a suggestion below or '
            "write your own.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        bubbles = []
        for msg in st.session_state.qa:
            role = "user" if msg["role"] == "user" else "ai"
            source = msg.get("source", "image")
            who = "You" if role == "user" else (
                "Assistant &middot; web search" if source == "web" else (
                "Assistant &middot; product filter" if source == "product_filter" else "Assistant &middot; image analysis"
                )
            )
            bubbles.append(
                f'<div class="pv-msg {role}"><div class="who">{who}</div>'
                f'{html.escape(msg["text"])}</div>'
            )
        st.markdown("".join(bubbles), unsafe_allow_html=True)

    theme.spacer(0.6)

    field, action = st.columns([4, 1])
    with field:
        question = st.text_input(
            "Question",
            key="qa_input",
            placeholder="Ask a question about this product...",
            label_visibility="collapsed",
        )
    with action:
        asked = st.button(
            "Ask AI",
            type="primary",
            **theme.STRETCH,
            disabled=not question.strip(),
        )

    if asked:
        _submit(question)
        st.rerun()

    st.markdown(
        '<div class="pv-eyebrow" style="margin-top:1rem">Try one of these</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(SUGGESTED_QUESTIONS), gap="small")
    for col, suggestion in zip(cols, SUGGESTED_QUESTIONS):
        with col:
            if st.button(suggestion, key=f"sq_{suggestion[:18]}", **theme.STRETCH):
                _submit(suggestion)
                st.rerun()
