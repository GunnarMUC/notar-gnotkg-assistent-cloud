"""Notar GNotKG Assistent – Haupt-App (Streamlit)."""

import streamlit as st

from ui.extraction import render_extraction_tab
from ui.invoice import render_invoice_tab
from ui.review import render_review_tab
from ui.sidebar import render_sidebar
from ui.state import init_session_state
from ui.upload import render_upload_tab

st.set_page_config(
    page_title="Notar GNotKG Assistent – Cloud",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------------------------
# Hauptbereich
# ---------------------------------------------------------------------------
st.title("⚖️ Notar GNotKG Assistent – Cloud")
st.caption("GNotKG-konforme Honorarrechnung aus Ihrer Urkunde – mit Cloud-LLM-Providern (API-Only)")
st.error(
    "⚠️ Diese Version verwendet ausschließlich externe Cloud-LLM-Provider. "
    "Jeder Nutzer benötigt seinen eigenen API-Key und trägt die Datenschutz-Verantwortung selbst."
)

# Workflow-Steps als Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "🔍 Extraktion", "✏️ Prüfung", "📄 Rechnung"])

with tab1:
    render_upload_tab()

with tab2:
    render_extraction_tab()

with tab3:
    render_review_tab()

with tab4:
    render_invoice_tab()
