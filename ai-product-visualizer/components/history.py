"""Past analyses."""

import streamlit as st

from components import media, theme
from components.state import go


def render_history() -> None:
    items = st.session_state.history

    head, action = st.columns([3, 1])
    with head:
        theme.section(
            "Analysis history",
            f"{len(items)} product{'' if len(items) == 1 else 's'} in this workspace."
            if items
            else "Nothing saved yet.",
        )
    with action:
        if st.button("Analyze product", type="primary", **theme.STRETCH):
            go("Analyze Product")

    if not items:
        st.markdown(
            '<div class="pv-empty"><h4>No product analyses yet</h4>'
            "<p>Upload your first product to get started.</p></div>",
            unsafe_allow_html=True,
        )
        return

    theme.spacer(0.4)

    for start in range(0, len(items), 3):
        cols = st.columns(3, gap="medium")
        for col, item in zip(cols, items[start:start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="pv-card" style="padding:0;overflow:hidden">
                      <img style="width:100%;height:140px;object-fit:cover;display:block"
                           src="{item.get('image_url') or media.image_data_uri(media.placeholder_image(item['tint'], 360, item['name']))}"/>
                      <div style="padding:1rem 1.15rem 1.15rem 1.15rem">
                        <h4 style="margin:0">{item['name']}</h4>
                        <p style="margin-top:.3rem">{item['category']}</p>
                        <p style="margin-top:.55rem;font-size:.78rem">{item['date']}</p>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "View analysis", key=f"hist_{item['id']}", **theme.STRETCH
                ):
                    st.session_state.analysis = item["analysis"]
                    st.session_state.analysis_source = item["name"]
                    st.session_state.upload = None
                    st.session_state.qa = []
                    go("Analyze Product")
        theme.spacer(0.9)
