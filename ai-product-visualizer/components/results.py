"""Analysis results dashboard."""

import streamlit as st

from components import media, theme
from components.qa import render_qa
from components.state import reset_analysis
from services.ai_service import search_product_prices


def _attribute_card(title: str, body_html: str) -> str:
    return (
        f'<div class="pv-card"><div class="pv-eyebrow">{title}</div>'
        f'<div style="margin-top:.2rem">{body_html}</div></div>'
    )


def render_results() -> None:
    analysis = st.session_state.analysis
    overview = analysis["overview"]
    identity = analysis.get("identity", {})
    if not identity:
        identity = {
            "brand": "",
            "product_name": overview.get("Product Type", ""),
            "model_number": "",
            "variant": overview.get("Primary Color", ""),
            "specifications": [],
        }
    attrs = analysis["attributes"]
    conf = analysis["confidence"]

    head, action = st.columns([3, 1])
    with head:
        theme.section(
            "Product analysis",
            f"Source image: {st.session_state.analysis_source or 'sample product'}",
        )
    with action:
        if st.button("New analysis", **theme.STRETCH):
            reset_analysis()
            st.rerun()

    left, right = st.columns([1.15, 1.35], gap="large")

    with left:
        image = st.session_state.upload
        if image is not None:
            st.image(image, **theme.STRETCH)
        else:
            st.image(media.placeholder_image("#8A93A3"), **theme.STRETCH)

    with right:
        theme.section("Product overview", eyebrow="Summary")
        theme.rows(overview.items())
        if identity:
            theme.spacer(0.6)
            theme.section("Product identity", "Review or correct these details before searching the market.", eyebrow="Search matching")
            identity_key = (st.session_state.analysis_source or "sample").replace(" ", "_")
            brand = st.text_input("Brand", value=identity.get("brand", ""), key=f"identity_brand_{identity_key}")
            product_name = st.text_input("Product name", value=identity.get("product_name", ""), key=f"identity_product_{identity_key}")
            model_number = st.text_input("Model number", value=identity.get("model_number", ""), key=f"identity_model_{identity_key}", placeholder="Leave blank if not visible")
            variant = st.text_input("Variant", value=identity.get("variant", ""), key=f"identity_variant_{identity_key}")
            specifications_text = st.text_input(
                "Visible specifications",
                value=", ".join(identity.get("specifications", [])),
                key=f"identity_specs_{identity_key}",
                help="Optional: storage, size, colorway, capacity, or other visible details.",
            )
            identity = {
                "brand": brand.strip(),
                "product_name": product_name.strip(),
                "model_number": model_number.strip(),
                "variant": variant.strip(),
                "specifications": [item.strip() for item in specifications_text.split(",") if item.strip()],
            }
        theme.spacer(0.7)

        st.markdown(
            f"""
            <div class="pv-card">
              <div class="pv-eyebrow">AI confidence</div>
              <div style="display:flex;align-items:baseline;justify-content:space-between">
                <span style="font-size:.9rem;font-weight:600">{conf['label']}</span>
                <span style="font-size:1.35rem;font-weight:700">{conf['score']}%</span>
              </div>
              <div class="pv-meter"><span style="width:{conf['score']}%"></span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    theme.spacer(2.0)
    theme.section("Visual attributes", "What the image shows, grouped by attribute.")

    swatches = {c["name"]: c["hex"] for c in attrs["Colors"]}
    color_html = theme.chips([c["name"] for c in attrs["Colors"]], swatches)

    row1 = st.columns(3, gap="medium")
    with row1[0]:
        st.markdown(_attribute_card("Colors", color_html), unsafe_allow_html=True)
    with row1[1]:
        st.markdown(
            _attribute_card("Material", theme.chips(attrs["Material"])),
            unsafe_allow_html=True,
        )
    with row1[2]:
        st.markdown(
            _attribute_card("Shape", theme.chips(attrs["Shape"])),
            unsafe_allow_html=True,
        )

    theme.spacer(0.9)
    row2 = st.columns([1, 2], gap="medium")
    with row2[0]:
        st.markdown(
            _attribute_card("Style", theme.chips(attrs["Style"])),
            unsafe_allow_html=True,
        )
    with row2[1]:
        st.markdown(
            _attribute_card("Features", theme.chips(attrs["Features"])),
            unsafe_allow_html=True,
        )

    theme.spacer(2.0)
    theme.section("AI product description", "A written summary of the same image.")
    st.markdown(
        f"""
        <div class="pv-card" style="padding:1.5rem 1.7rem">
          <p style="font-size:.95rem;line-height:1.75;color:#DCE2EA;max-width:74ch">
            {analysis['description']}
          </p>
          <div style="margin-top:1.1rem;padding-top:.9rem;border-top:1px solid var(--border)">
              <span class="pv-pill">Generated from the configured Foundry model</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confident, unknown = st.columns(2, gap="medium")
    with confident:
        items = analysis.get("confidently_identified", [])
        st.markdown(_attribute_card("Confidently identified", theme.chips(items) or "None"), unsafe_allow_html=True)
    with unknown:
        items = analysis.get("cannot_determine", [])
        st.markdown(_attribute_card("Cannot determine", theme.chips(items) or "None"), unsafe_allow_html=True)

    theme.spacer(1.2)
    theme.section("Current market prices", "Search the web for prices and comparable products.")
    location = st.text_input(
        "Market or location",
        value="India",
        key="price_location",
        help="Prices and availability vary by country and location.",
    )
    exact_identity_ready = all(identity.get(field) for field in ("brand", "product_name", "model_number"))
    if exact_identity_ready:
        st.success("Exact-match search ready: brand, product name, and model number are available.")
    else:
        st.warning("The model number is not verified. Results will be comparable products, not confirmed exact matches.")

    if st.button("Search current prices", type="primary", disabled=not identity.get("product_name")):
        with st.spinner("Searching current prices..."):
            try:
                st.session_state.web_search_result = search_product_prices(
                    identity, location, exact_match=exact_identity_ready
                )
            except Exception as exc:
                st.session_state.web_search_result = f"Web search failed: {exc}"
    if st.session_state.web_search_result:
        st.markdown(st.session_state.web_search_result)

    theme.spacer(2.0)
    render_qa()
