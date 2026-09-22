"""Design tokens, global stylesheet and small reusable UI primitives.

Everything visual lives here so the rest of the app stays readable.
"""

import streamlit as st

COLORS = {
    "bg": "#0B0F14",
    "bg_alt": "#11161D",
    "card": "#151B23",
    "border": "#252D38",
    "text": "#F5F7FA",
    "muted": "#9AA4B2",
    "accent": "#7C5CFF",
    "accent_hover": "#9278FF",
    "success": "#35D07F",
    "warning": "#F5B942",
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg: #0B0F14;
  --bg-alt: #11161D;
  --card: #151B23;
  --border: #252D38;
  --text: #F5F7FA;
  --muted: #9AA4B2;
  --accent: #7C5CFF;
  --accent-hover: #9278FF;
  --success: #35D07F;
  --warning: #F5B942;
  --accent-soft: rgba(124,92,255,.13);
  --hero-glow: rgba(124,92,255,.18);
  --radius: 14px;
  --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.22);
}

html, body, .stApp, [class*="st-emotion"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp { background: var(--bg); color: var(--text); }

/* Activated by the theme toggle in the sidebar. */
.stApp:has(.pv-light-marker) {
  --bg: #F5F7FB;
  --bg-alt: #FFFFFF;
  --card: #FFFFFF;
  --border: #E5E9F0;
  --text: #172033;
  --muted: #657087;
  --accent: #6750E8;
  --accent-hover: #5740D1;
  --accent-soft: rgba(103,80,232,.10);
  --hero-glow: rgba(103,80,232,.12);
  --shadow: 0 1px 2px rgba(31,41,55,.04), 0 14px 34px rgba(31,41,55,.08);
}

/* --- strip default streamlit chrome --- */
#MainMenu, footer, header [data-testid="stStatusWidget"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stToolbar"] { right: 8px; }

.block-container {
  max-width: 1240px;
  padding: 2.6rem 2.5rem 5rem 2.5rem;
}

/* --- typography --- */
h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.02em; font-weight: 600; }
p, span, li, label { color: var(--text); }

.pv-eyebrow {
  font-size: .72rem; font-weight: 600; letter-spacing: .09em;
  color: var(--muted); text-transform: uppercase; margin-bottom: .6rem;
}
.pv-section-title { font-size: 1.05rem; font-weight: 600; margin: 0 0 .15rem 0; }
.pv-section-sub { font-size: .87rem; color: var(--muted); margin: 0 0 1rem 0; }
.pv-muted { color: var(--muted); }

/* --- app header --- */
.pv-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 2rem; padding-bottom: 1.1rem; margin-bottom: 1.6rem;
  border-bottom: 1px solid var(--border);
}
.pv-header h1 { font-size: 1.8rem; margin: 0 0 .3rem 0; letter-spacing: -.04em; }
.pv-header p { color: var(--muted); font-size: .92rem; margin: 0; }
.pv-header-meta { display: flex; align-items: center; gap: .55rem; flex-shrink: 0; }

.pv-pill {
  display: inline-flex; align-items: center; gap: .45rem;
  background: var(--bg-alt); border: 1px solid var(--border);
  border-radius: 999px; padding: .38rem .8rem;
  font-size: .78rem; color: var(--muted); white-space: nowrap;
}
.pv-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--success); }
.pv-dot.idle { background: var(--muted); }

/* --- cards --- */
.pv-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.15rem 1.25rem;
  box-shadow: var(--shadow); height: 100%;
  transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
}
.pv-card:hover { border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,.12); }
.pv-card h4 { font-size: .97rem; margin: 0 0 .4rem 0; }
.pv-card p { font-size: .85rem; color: var(--muted); line-height: 1.55; margin: 0; }

.pv-card-icon {
  width: 34px; height: 34px; border-radius: 10px; margin-bottom: .85rem;
  background: var(--accent-soft); border: 1px solid rgba(124,92,255,.28);
  display: flex; align-items: center; justify-content: center;
}
.pv-card-icon svg { width: 17px; height: 17px; stroke: var(--accent); }

/* --- hero --- */
.pv-hero {
  background:
    radial-gradient(600px 300px at 8% -30%, var(--hero-glow), transparent 70%),
    linear-gradient(120deg, var(--bg-alt), var(--card));
  border: 1px solid var(--border); border-radius: 22px;
  padding: 3.4rem 3rem 3rem 3rem; margin-bottom: 1.25rem;
  position: relative; overflow: hidden;
}
.pv-hero:after { content: '✦'; position: absolute; right: 7%; top: 18%; font-size: 7rem; line-height: 1; color: var(--accent); opacity: .10; transform: rotate(18deg); }
.pv-hero h2 { font-size: 2.45rem; line-height: 1.08; margin: 0 0 .85rem 0; max-width: 18ch; letter-spacing: -.055em; position: relative; z-index: 1; }
.pv-hero p { color: var(--muted); font-size: .95rem; line-height: 1.6; max-width: 62ch; margin: 0; }

/* --- data rows / chips --- */
.pv-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: .72rem 0; border-bottom: 1px solid var(--border);
}
.pv-row:last-child { border-bottom: none; }
.pv-row .k { font-size: .83rem; color: var(--muted); }
.pv-row .v { font-size: .87rem; font-weight: 500; }

.pv-chip {
  display: inline-flex; align-items: center; gap: .45rem;
  background: #1A212B; border: 1px solid var(--border); border-radius: 8px;
  padding: .34rem .66rem; font-size: .8rem; margin: 0 .4rem .45rem 0;
}
.pv-swatch { width: 11px; height: 11px; border-radius: 3px; border: 1px solid rgba(255,255,255,.18); }

.pv-stat { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: .9rem 1rem; }
.pv-stat .k { font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.pv-stat .v { font-size: 1rem; font-weight: 600; margin-top: .3rem; }

/* --- confidence meter --- */
.pv-meter { height: 6px; border-radius: 99px; background: #1E2733; overflow: hidden; margin-top: .9rem; }
.pv-meter span { display: block; height: 100%; border-radius: 99px; background: var(--accent); }

/* --- chat --- */
.pv-msg { border-radius: 12px; padding: .8rem 1rem; margin-bottom: .6rem; font-size: .88rem; line-height: 1.6; }
.pv-msg.user { background: rgba(124,92,255,.10); border: 1px solid rgba(124,92,255,.26); margin-left: 12%; }
.pv-msg.ai { background: var(--card); border: 1px solid var(--border); margin-right: 12%; }
.pv-msg .who {
  font-size: .68rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--muted); margin-bottom: .35rem; display: flex; gap: .5rem; align-items: center;
}

/* --- empty state --- */
.pv-empty {
  border: 1px dashed var(--border); border-radius: var(--radius);
  background: linear-gradient(135deg, var(--bg-alt), var(--card)); padding: 3.6rem 2rem; text-align: center;
}
.pv-empty h4 { font-size: 1rem; margin: 0 0 .4rem 0; }
.pv-empty p { color: var(--muted); font-size: .87rem; margin: 0; }

/* --- buttons --- */
.stButton > button, .stDownloadButton > button {
  border-radius: 10px; font-weight: 500; font-size: .87rem;
  padding: .5rem 1.05rem; transition: all .16s ease; box-shadow: none;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--accent), #8D6BFF); border: 1px solid var(--accent); color: #fff;
}
.stButton > button[kind="primary"]:hover:not(:disabled) {
  background: var(--accent-hover); border-color: var(--accent-hover);
}
.stButton > button[kind="secondary"] {
  background: var(--card); border: 1px solid var(--border); color: var(--text);
}
.stButton > button[kind="secondary"]:hover:not(:disabled) { border-color: #3B4655; color: var(--text); }
.stButton > button:disabled { opacity: .45; cursor: not-allowed; }
.stButton > button:focus-visible { outline: 2px solid var(--accent-hover); outline-offset: 2px; }

/* --- sidebar --- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--bg-alt), var(--bg)); border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
[data-testid="stSidebarNav"], [data-testid="stSidebarCollapseButton"] { display: none; }

.pv-brand { display: flex; align-items: center; gap: .65rem; padding: 0 .35rem 1.1rem .35rem; }
.pv-brand-mark {
  width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
  background: linear-gradient(140deg, #7C5CFF, #5B3FE0);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: .82rem; color: #fff;
}
.pv-brand-name { font-size: .92rem; font-weight: 600; line-height: 1.2; }
.pv-brand-sub { font-size: .7rem; color: var(--muted); }

.pv-navlabel {
  font-size: .68rem; letter-spacing: .1em; text-transform: uppercase;
  color: var(--muted); padding: .2rem .35rem .5rem .35rem;
}

/* sidebar nav buttons */
.st-key-pv_nav .stButton > button {
  width: 100%; justify-content: flex-start; text-align: left;
  background: transparent; border: 1px solid transparent; color: var(--muted);
  padding: .48rem .7rem; margin-bottom: .12rem; font-weight: 500;
}
.st-key-pv_nav .stButton > button:hover { background: #18202A; color: var(--text); }
.st-key-pv_nav .stButton > button[kind="primary"] {
  background: rgba(124,92,255,.13); border-color: rgba(124,92,255,.30); color: var(--text);
}
.st-key-pv_nav .stButton > button[kind="primary"]:hover { background: rgba(124,92,255,.18); }

/* Streamlit renders button labels inside nested elements, so explicitly inherit
   the theme color to keep navigation readable in light mode. */
.st-key-pv_nav button,
.st-key-pv_nav button p,
.st-key-pv_nav button span { color: var(--text) !important; }
.pv-brand-name { color: var(--text); }

.stApp:has(.pv-light-marker) .st-key-pv_nav button[data-testid="stBaseButton-secondary"],
.stApp:has(.pv-light-marker) .st-key-pv_nav button[kind="secondary"] {
  background: #FFFFFF !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
}
.stApp:has(.pv-light-marker) .st-key-pv_nav button,
.stApp:has(.pv-light-marker) .st-key-pv_nav button p,
.stApp:has(.pv-light-marker) .st-key-pv_nav button span {
  background: #FFFFFF !important;
  color: #172033 !important;
}
.stApp:has(.pv-light-marker) .st-key-pv_nav button[data-testid="stBaseButton-primary"],
.stApp:has(.pv-light-marker) .st-key-pv_nav button[kind="primary"] {
  background: linear-gradient(135deg, #7658F5, #8D6BFF) !important;
  border-color: #7658F5 !important;
  color: #FFFFFF !important;
}
.stApp:has(.pv-light-marker) .st-key-pv_nav button[data-testid="stBaseButton-primary"] p,
.stApp:has(.pv-light-marker) .st-key-pv_nav button[kind="primary"] p,
.stApp:has(.pv-light-marker) .st-key-pv_nav button[data-testid="stBaseButton-primary"] span,
.stApp:has(.pv-light-marker) .st-key-pv_nav button[kind="primary"] span {
  color: #FFFFFF !important;
}
.stApp:has(.pv-light-marker) .st-key-pv_nav button[data-testid="stBaseButton-primary"] p,
.stApp:has(.pv-light-marker) .st-key-pv_nav button[kind="primary"] p,
.stApp:has(.pv-light-marker) .st-key-pv_nav button[data-testid="stBaseButton-primary"] span,
.stApp:has(.pv-light-marker) .st-key-pv_nav button[kind="primary"] span {
  background: transparent !important;
  color: #FFFFFF !important;
}

.pv-sidefoot {
  border: 1px solid var(--border); background: var(--card);
  border-radius: 12px; padding: .8rem .9rem; margin: .4rem .35rem 0 .35rem;
}
.pv-sidefoot .k { font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.pv-sidefoot .v { font-size: .84rem; font-weight: 600; margin: .25rem 0 .6rem 0; }
.pv-sidefoot .s { font-size: .78rem; color: var(--muted); display: flex; align-items: center; gap: .45rem; }

[data-testid="stSidebar"] [data-testid="stToggle"] { margin: .35rem .35rem .6rem; }
[data-testid="stSidebar"] [data-testid="stToggle"] label { color: var(--muted); font-size: .78rem; }

/* --- file uploader --- */
[data-testid="stFileUploaderDropzone"] {
  background: var(--bg-alt); border: 1.5px dashed var(--border);
  border-radius: var(--radius); padding: 2.4rem 1.5rem;
  transition: border-color .18s ease, background .18s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: rgba(124,92,255,.55); background: #131A23;
}
[data-testid="stFileUploaderDropzone"] small { color: var(--muted); }
[data-testid="stFileUploaderDropzone"] button {
  background: var(--card); border: 1px solid var(--border);
  color: var(--text); border-radius: 9px;
}
[data-testid="stFileUploaderDropzone"] button:hover { border-color: var(--accent); color: var(--text); }
[data-testid="stFileUploaderFile"] { color: var(--muted); }

/* --- inputs --- */
.stTextInput input {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); font-size: .88rem; padding: .6rem .85rem;
}
.stTextInput input::placeholder { color: #6C7787; }
.stTextInput input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(124,92,255,.14); }

/* --- images --- */
[data-testid="stImage"] img, .pv-thumb {
  border-radius: 12px; border: 1px solid var(--border);
}

/* --- misc --- */
hr, [data-testid="stDivider"] { border-color: var(--border); }
[data-testid="stAlert"] { border-radius: 12px; font-size: .86rem; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stToast"] { background: var(--card); border: 1px solid var(--border); }

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
@media (max-width: 900px) {
  .block-container { padding: 1.4rem 1rem 3rem 1rem; }
  .pv-hero { padding: 1.8rem 1.4rem; }
  .pv-hero h2 { font-size: 1.6rem; }
  .pv-header { flex-direction: column; gap: .9rem; }
}
@media (max-width: 640px) {
  /* Keep every element inside the phone viewport. */
  .block-container {
    width: 100% !important;
    max-width: 100% !important;
    padding: 1rem .75rem 2.5rem .75rem !important;
  }
  [data-testid="stAppViewContainer"] {
    overflow-x: hidden;
  }

  /* Streamlit columns become single-column sections on small screens. */
  [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: .75rem !important;
  }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    flex: 1 1 100% !important;
    width: 100% !important;
    min-width: 100% !important;
  }

  .pv-header {
    gap: .65rem;
    padding-bottom: .85rem;
    margin-bottom: 1.1rem;
  }
  .pv-header h1 {
    font-size: 1.35rem;
    line-height: 1.2;
  }
  .pv-header p { font-size: .82rem; line-height: 1.45; }
  .pv-header-meta { width: 100%; flex-wrap: wrap; }

  .pv-hero {
    padding: 1.35rem 1rem;
    border-radius: 16px;
  }
  .pv-hero:after { display: none; }
  .pv-hero h2 {
    font-size: 1.65rem;
    line-height: 1.12;
    max-width: none;
  }
  .pv-hero p { font-size: .86rem; }

  .pv-card {
    min-width: 0;
    padding: .95rem 1rem;
    border-radius: 12px;
  }
  .pv-card:hover {
    transform: none;
  }
  .pv-section-title { font-size: 1rem; }
  .pv-section-sub { font-size: .8rem; line-height: 1.4; }

  .pv-row {
    align-items: flex-start;
    gap: .75rem;
  }
  .pv-row .k { flex: 0 0 36%; }
  .pv-row .v {
    min-width: 0;
    text-align: right;
    overflow-wrap: anywhere;
  }
  .pv-pill {
    white-space: normal;
    line-height: 1.25;
    padding: .35rem .65rem;
  }
  .pv-chip { max-width: 100%; overflow-wrap: anywhere; }

  /* Make primary actions easy to tap and readable on small screens. */
  .stButton > button,
  .stDownloadButton > button {
    min-height: 2.75rem;
    width: 100%;
    white-space: normal;
    line-height: 1.25;
    padding: .65rem .8rem;
  }
  .stTextInput input {
    min-height: 2.75rem;
    font-size: 1rem;
  }
  [data-testid="stFileUploaderDropzone"] {
    padding: 1.35rem .8rem;
  }
  [data-testid="stFileUploaderDropzoneInstructions"] {
    text-align: center;
  }
  [data-testid="stImage"] img,
  .pv-thumb {
    max-width: 100%;
    height: auto !important;
  }

  /* Chat messages use the full available width on phones. */
  .pv-msg.user,
  .pv-msg.ai {
    margin-left: 0;
    margin-right: 0;
    padding: .75rem .8rem;
    font-size: .84rem;
  }
  .pv-empty { padding: 2.4rem 1rem; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    if st.session_state.get("theme_mode") == "light":
        st.markdown(
            """
            <style>
            .st-key-pv_nav .stButton > button {
              background: #FFFFFF !important;
              border: 1px solid #E5E9F0 !important;
              color: #172033 !important;
            }
            .st-key-pv_nav .stButton > button p,
            .st-key-pv_nav .stButton > button span {
              background: transparent !important;
              color: #172033 !important;
            }
            .st-key-pv_nav .stButton > button[kind="primary"] {
              background: linear-gradient(135deg, #7658F5, #8D6BFF) !important;
              border-color: #7658F5 !important;
              color: #FFFFFF !important;
            }
            .st-key-pv_nav .stButton > button[kind="primary"] p,
            .st-key-pv_nav .stButton > button[kind="primary"] span {
              color: #FFFFFF !important;
            }
            .pv-brand-name { color: #172033 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def _supports_width_kwarg() -> bool:
    try:
        major, minor = (int(part) for part in st.__version__.split(".")[:2])
    except Exception:
        return False
    return (major, minor) >= (1, 49)


# `use_container_width` is deprecated in newer Streamlit builds; this keeps the
# app warning-free on both old and new versions.
STRETCH = {"width": "stretch"} if _supports_width_kwarg() else {"use_container_width": True}


# --- small primitives -------------------------------------------------------

def section(title: str, subtitle: str = "", eyebrow: str = "") -> None:
    """Section heading with an optional eyebrow and subtitle."""
    html = ""
    if eyebrow:
        html += f'<div class="pv-eyebrow">{eyebrow}</div>'
    html += f'<div class="pv-section-title">{title}</div>'
    if subtitle:
        html += f'<div class="pv-section-sub">{subtitle}</div>'
    st.markdown(html, unsafe_allow_html=True)


def card(title: str, body: str, icon: str = "") -> None:
    icon_html = f'<div class="pv-card-icon">{icon}</div>' if icon else ""
    st.markdown(
        f'<div class="pv-card">{icon_html}<h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def rows(pairs) -> None:
    """Key/value list inside a card."""
    inner = "".join(
        f'<div class="pv-row"><span class="k">{k}</span><span class="v">{v}</span></div>'
        for k, v in pairs
    )
    st.markdown(f'<div class="pv-card">{inner}</div>', unsafe_allow_html=True)


def chips(values, swatches=None) -> str:
    """Return chip markup. `swatches` maps a value to a hex colour dot."""
    out = []
    for v in values:
        dot = ""
        if swatches and v in swatches:
            dot = f'<span class="pv-swatch" style="background:{swatches[v]}"></span>'
        out.append(f'<span class="pv-chip">{dot}{v}</span>')
    return "".join(out)


def spacer(height: float = 1.0) -> None:
    st.markdown(f'<div style="height:{height}rem"></div>', unsafe_allow_html=True)
