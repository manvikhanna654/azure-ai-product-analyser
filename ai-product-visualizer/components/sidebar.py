"""Left navigation rail."""

import streamlit as st

from components import theme
from components.state import PAGES

_NAV_HINT = {
    "Dashboard": "Overview",
    "Analyze Product": "Upload and analyse",
    "History": "Past analyses",
    "About": "Project details",
}


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="pv-brand">
              <div class="pv-brand-mark">PV</div>
              <div>
                <div class="pv-brand-name">AI Product Visualizer</div>
                <div class="pv-brand-sub">Visual product analysis</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="pv-navlabel">Navigate</div>', unsafe_allow_html=True)

        with st.container(key="pv_nav"):
            for page in PAGES:
                active = st.session_state.page == page
                if st.button(
                    page,
                    key=f"nav_{page}",
                    **theme.STRETCH,
                    type="primary" if active else "secondary",
                    help=_NAV_HINT[page],
                ):
                    if not active:
                        st.session_state.page = page
                        st.rerun()

        st.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)

        is_light = st.session_state.theme_mode == "light"
        if st.toggle("Light theme", value=is_light, key="theme_toggle"):
            if st.session_state.theme_mode != "light":
                st.session_state.theme_mode = "light"
                st.rerun()
        elif st.session_state.theme_mode != "dark":
            st.session_state.theme_mode = "dark"
            st.rerun()
        if st.session_state.theme_mode == "light":
            st.markdown('<span class="pv-light-marker"></span>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="pv-sidefoot">
              <div class="k">AI model</div>
              <div class="v">GPT-4.1-mini</div>
              <div class="s"><span class="pv-dot idle"></span> Not connected yet</div>
            </div>
            <div style="padding:.9rem .35rem 0 .35rem;font-size:.72rem;color:#6C7787;line-height:1.5">
              Interface preview. Model integration is not wired up.
            </div>
            """,
            unsafe_allow_html=True,
        )
