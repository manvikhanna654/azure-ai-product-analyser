"""Upload step of the Analyze Product page."""

import streamlit as st
from PIL import Image

from components import theme
from data.mock_data import new_history_entry
from services.ai_service import analyze_product


MAX_MB = 10
ACCEPTED = ["jpg", "jpeg", "png", "webp"]


def _readable_size(num_bytes: int) -> str:
    """Convert bytes into a readable file size."""
    kb = num_bytes / 1024

    if kb < 1024:
        return f"{kb:.0f} KB"

    return f"{kb / 1024:.2f} MB"


def render_upload() -> None:
    """Render the product image upload section."""

    theme.section(
        "Analyze your product",
        "Upload a clear product image to generate AI-powered insights.",
    )

    st.markdown(
        '<div class="pv-eyebrow" style="margin-top:.4rem">'
        "Upload product image"
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # IMAGE UPLOADER
    # ---------------------------------------------------------
    upload = st.file_uploader(
        "",
        type=ACCEPTED,
        label_visibility="collapsed",
        help="JPG, JPEG, PNG or WEBP up to 10 MB.",
    )

    st.markdown(
        '<div style="display:flex;gap:.5rem;margin-top:.7rem;'
        'flex-wrap:wrap">'
        '<span class="pv-pill">Formats: JPG, JPEG, PNG, WEBP</span>'
        f'<span class="pv-pill">Maximum size: {MAX_MB} MB</span>'
        '<span class="pv-pill">One product per image works best</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # NO IMAGE SELECTED
    # ---------------------------------------------------------
    if upload is None:
        st.session_state.upload = None

        theme.spacer(1.6)

        left, right = st.columns([1, 1], gap="medium")

        with left:
            theme.card(
                "Before you upload",
                "Fill the frame with a single product, keep the background "
                "plain and avoid heavy shadows. Sharper images give cleaner "
                "attributes.",
            )

        with right:
            theme.card(
                "What you get back",
                "A product overview, visual attributes, a written description "
                "and a question panel tied to the same image.",
            )

        st.button(
            "Analyze product",
            type="primary",
            disabled=True,
        )

        st.caption("Select an image to enable analysis.")

        return

    # ---------------------------------------------------------
    # FILE SIZE VALIDATION
    # ---------------------------------------------------------
    size_mb = upload.size / (1024 * 1024)

    if size_mb > MAX_MB:
        st.error(
            f"That file is {size_mb:.1f} MB. "
            f"Upload an image under {MAX_MB} MB."
        )
        return

    # ---------------------------------------------------------
    # IMAGE VALIDATION
    # ---------------------------------------------------------
    try:
        image = Image.open(upload)
        image.load()

    except Exception:
        st.error(
            "That file could not be read as an image. "
            "Try a JPG, PNG or WEBP image."
        )
        return

    # Save image in session state
    st.session_state.upload = image

    # ---------------------------------------------------------
    # PRODUCT PREVIEW
    # ---------------------------------------------------------
    theme.spacer(1.4)

    left, right = st.columns(
        [1.35, 1],
        gap="large",
    )

    with left:
        st.image(
            image,
            **theme.STRETCH,
        )

    with right:

        theme.section(
            "Product preview",
            eyebrow="Ready to analyse",
        )

        theme.rows(
            [
                ("File name", upload.name),
                (
                    "Dimensions",
                    f"{image.width} × {image.height} px",
                ),
                (
                    "File size",
                    _readable_size(upload.size),
                ),
                (
                    "Format",
                    (
                        image.format
                        or upload.type.split("/")[-1]
                    ).upper(),
                ),
            ]
        )

        theme.spacer(0.8)

        # -----------------------------------------------------
        # ANALYZE BUTTON
        # -----------------------------------------------------
        if st.button(
            "Analyze product",
            type="primary",
            **theme.STRETCH,
        ):
            _run_analysis(
                upload.name,
                upload.getvalue(),
                upload.type,
            )

        st.caption(
            "The image will be analyzed by your configured "
            "Foundry model."
        )


def _run_analysis(
    file_name: str,
    image_bytes: bytes,
    mime_type: str,
) -> None:
    """Send the uploaded image to Microsoft Foundry."""

    with st.spinner("Analyzing product..."):

        try:
            analysis = analyze_product(
                image_bytes,
                mime_type,
            )

        except Exception as exc:
            st.error(
                f"Could not analyze the image: {exc}"
            )
            return

    # ---------------------------------------------------------
    # SAVE ANALYSIS
    # ---------------------------------------------------------
    st.session_state.analysis = analysis

    st.session_state.analysis_source = file_name

    st.session_state.upload_bytes = image_bytes

    st.session_state.upload_mime = mime_type

    st.session_state.qa = []

    # ---------------------------------------------------------
    # SAVE TO HISTORY
    # ---------------------------------------------------------
    st.session_state.history.insert(
        0,
        new_history_entry(
            analysis["overview"]["Product Type"],
            analysis,
        ),
    )

    st.session_state.toast = "Analysis ready"

    # Reload the page and show the analysis
    st.rerun()
