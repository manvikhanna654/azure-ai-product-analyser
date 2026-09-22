"""AI Product Visualizer — interface preview.

Run with:  streamlit run app.py
"""

import streamlit as st

from components import theme
from components.about import render_about
from components.dashboard import render_dashboard
from components.header import render_header
from components.history import render_history
from components.results import render_results
from components.sidebar import render_sidebar
from components.state import init_state
from components.upload import render_upload

st.set_page_config(
    page_title="AI Product Visualizer",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

HEADINGS = {
    "Dashboard": (
        "AI Product Visualizer",
        "Turn any product image into structured AI-powered product insights.",
    ),
    "Analyze Product": (
        "Analyze product",
        "Upload an image and review the attributes pulled from it.",
    ),
    "History": (
        "History",
        "Products analysed in this workspace.",
    ),
    "About": (
        "About",
        "How the project is built and what it is meant to do.",
    ),
}


def main() -> None:
    init_state()
    theme.inject_css()
    render_sidebar()

    page = st.session_state.page
    render_header(*HEADINGS[page])

    if st.session_state.toast:
        st.toast(st.session_state.toast)
        st.session_state.toast = None

    if page == "Dashboard":
        render_dashboard()
    elif page == "Analyze Product":
        if st.session_state.analysis:
            render_results()
        else:
            render_upload()
    elif page == "History":
        render_history()
    else:
        render_about()


if __name__ == "__main__":
    main()
