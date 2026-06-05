import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', 'Outfit', sans-serif;
    background-color: #05070f;
}

/* ── Aurora background on main content ──────────────────────────────────── */
.main .block-container {
    background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,0.12) 0%, transparent 60%),
                radial-gradient(ellipse 50% 40% at 90% 80%, rgba(56,189,248,0.07) 0%, transparent 50%),
                radial-gradient(ellipse 40% 30% at 10% 90%, rgba(167,139,250,0.08) 0%, transparent 50%),
                #05070f;
    padding-top: 1.5rem;
}

/* ── Brand title ─────────────────────────────────────────────────────────── */
.spark-title {
    background: linear-gradient(135deg, #c4b5fd 0%, #818cf8 35%, #38bdf8 70%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 900;
    font-size: 2.8rem;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 0;
    font-family: 'Outfit', sans-serif;
    text-shadow: none;
    filter: drop-shadow(0 0 32px rgba(129,140,248,0.4));
}

/* ── Tabs — pill style ───────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 6px;
    border-bottom: 1px solid rgba(99,102,241,0.25);
    padding-bottom: 4px;
}
[data-testid="stTabs"] button[role="tab"] {
    background: rgba(30,27,75,0.4) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px;
    padding: 6px 18px !important;
    transition: all 0.2s ease;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(56,189,248,0.15)) !important;
    border-color: rgba(129,140,248,0.6) !important;
    color: #e2e8f0 !important;
    box-shadow: 0 0 16px rgba(99,102,241,0.25), inset 0 1px 0 rgba(255,255,255,0.08);
}
[data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.35) !important;
    color: #c4b5fd !important;
}

/* ── Section headers ────────────────────────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: -0.3px;
}
h2 {
    font-size: 1.35rem !important;
    color: #e2e8f0 !important;
    font-weight: 700 !important;
    border-left: 3px solid #6366f1;
    padding-left: 18px !important;
    margin-top: 0.9rem !important;
    margin-bottom: 1.5rem !important;
}
h3 {
    font-size: 1.05rem !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.78rem !important;
}

/* ── Bento card — wraps expanders, metrics, sections ────────────────────── */
[data-testid="stExpander"] {
    background: rgba(15,17,35,0.7) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
    backdrop-filter: blur(8px);
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    color: #a5b4fc !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

/* ── Metrics row (dashboard) ────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(15,17,35,0.8) !important;
    border: 1px solid rgba(99,102,241,0.18) !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(129,140,248,0.4) !important;
    box-shadow: 0 2px 20px rgba(99,102,241,0.15);
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Brutalist terminal log ──────────────────────────────────────────────── */
.terminal-window {
    background: #000;
    color: #c8c8c8;
    padding: 16px 20px;
    border-radius: 4px;
    min-height: 300px;
    max-height: 560px;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.79rem;
    line-height: 1.7;
    border: 2px solid #1a1a2e;
    border-left: 4px solid #6366f1;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 0 40px rgba(99,102,241,0.12), inset 0 0 60px rgba(0,0,0,0.5);
    letter-spacing: 0.02em;
}
.terminal-window::-webkit-scrollbar { width: 6px; }
.terminal-window::-webkit-scrollbar-track { background: #0a0a0a; }
.terminal-window::-webkit-scrollbar-thumb { background: #2d2d4a; border-radius: 3px; }

/* Log-line colour coding */
.log-init     { color: #475569; }
.log-tools    { color: #818cf8; font-weight: 500; }
.log-llm      { color: #f1f5f9; }
.log-thinking { color: #64748b; font-style: italic; }
.log-tool     { color: #fbbf24; font-weight: 600; }
.log-result   { color: #34d399; }
.log-warn     { color: #f87171; }
.log-done     { color: #a5b4fc; font-weight: 600; }
.log-val      { color: #38bdf8; }
.log-cancel   { color: #f43f5e; font-weight: bold; text-transform: uppercase; }
.log-tokens   { color: #7c3aed; font-size: 0.72rem; opacity: 0.9; }

/* ── Inputs & text areas ─────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(10,10,20,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(129,140,248,0.6) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
    outline: none !important;
}

/* ── Selectbox ──────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(10,10,20,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
div.stButton > button {
    background: rgba(20,20,40,0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 8px !important;
    color: #a5b4fc !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px;
    transition: all 0.18s ease;
}
div.stButton > button:hover {
    background: rgba(99,102,241,0.18) !important;
    border-color: rgba(129,140,248,0.55) !important;
    color: #c4b5fd !important;
    box-shadow: 0 0 14px rgba(99,102,241,0.2);
}

/* Primary (Run Evaluation) */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #38bdf8 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 50%, #67e8f9 100%) !important;
    box-shadow: 0 6px 28px rgba(99,102,241,0.55);
    transform: translateY(-1px);
}

/* Cancel button */
.cancel-btn > div.stButton > button {
    background: rgba(127,29,29,0.6) !important;
    border-color: rgba(239,68,68,0.4) !important;
    color: #fca5a5 !important;
}

/* ── Pass / fail badges ──────────────────────────────────────────────────── */
.badge-pass {
    background: linear-gradient(135deg, #052e16, #064e2b);
    color: #4ade80;
    padding: 3px 12px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.8px;
    border: 1px solid rgba(74,222,128,0.25);
}
.badge-fail {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    color: #f87171;
    padding: 3px 12px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.8px;
    border: 1px solid rgba(248,113,113,0.25);
}
.badge-na {
    background: rgba(30,41,59,0.8);
    color: #64748b;
    padding: 3px 12px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.8px;
    border: 1px solid rgba(100,116,139,0.2);
}

/* ── Status pills ────────────────────────────────────────────────────────── */
.status-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    margin-right: 8px;
    letter-spacing: 0.2px;
    font-family: 'Space Grotesk', sans-serif;
}
.status-pill-up {
    background: rgba(5,46,22,0.8);
    color: #4ade80;
    border: 1px solid rgba(74,222,128,0.3);
    box-shadow: 0 0 10px rgba(74,222,128,0.1);
}
.status-pill-down {
    background: rgba(69,10,10,0.8);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.3);
}
.status-pill-wait {
    background: rgba(28,25,23,0.8);
    color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.3);
}

/* ── Model-mismatch warning pulse ────────────────────────────────────────── */
.model-mismatch {
    animation: pulse-warn 2s ease-in-out infinite;
}
@keyframes pulse-warn {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.75; }
}

/* ── Dashboard category headers ──────────────────────────────────────────── */
.cat-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    margin: 14px 0 6px;
    display: inline-block;
}

/* ── Dividers ────────────────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(99,102,241,0.15) !important;
    margin: 1.2rem 0 !important;
}

/* ── Code blocks ─────────────────────────────────────────────────────────── */
code {
    background: rgba(99,102,241,0.12) !important;
    color: #a5b4fc !important;
    border-radius: 4px !important;
    font-size: 0.82em !important;
    padding: 1px 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Captions ────────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] {
    color: #475569 !important;
    font-size: 0.76rem !important;
}

/* ── Info/warning/error boxes ────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

/* ── Download button ─────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: rgba(15,17,35,0.8) !important;
    border: 1px solid rgba(56,189,248,0.3) !important;
    color: #38bdf8 !important;
    border-radius: 8px !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(56,189,248,0.12) !important;
    border-color: rgba(56,189,248,0.5) !important;
    box-shadow: 0 0 14px rgba(56,189,248,0.15);
}

/* ── Checkbox ────────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    color: #94a3b8 !important;
    font-size: 0.84rem !important;
}

/* ── Slider ──────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: #a5b4fc !important;
}

/* ── Number input ────────────────────────────────────────────────────────── */
[data-testid="stNumberInput"] input {
    background: rgba(10,10,20,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Hide deploy button ──────────────────────────────────────────────────── */
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
.stAppDeployButton,
button[aria-label="Deploy this app"],
button[kind="header"] { display: none !important; }

/* ── Detect button alignment ─────────────────────────────────────────────── */
div[data-testid="column"] > div > div.stButton > button {
    margin-top: 0;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: #818cf8 !important;
}
</style>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
