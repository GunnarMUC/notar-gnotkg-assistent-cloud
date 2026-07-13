"""Session-State-Management für die Streamlit-App."""

from typing import Any

import streamlit as st

from core.config import get_settings
from core.llm_providers import get_default_model

settings = get_settings()

DEFAULTS: dict[str, Any] = {
    "notary_profile": None,
    "parsed_document": None,
    "extraction_result": None,
    "final_positions": [],
    "generated_invoice": None,
    "generated_audit": None,
    "auslagen": {"dokumentenpauschale": 0.0, "post_telekom": 0.0, "sonstige": 0.0},
    "llm_provider": settings.llm_provider,
    "llm_model": settings.llm_model or get_default_model(settings.llm_provider),
    "provider_keys": {},
    "_last_provider": None,
    "gnotkg_status": None,
    "workflow_step": "upload",  # upload | preview | extraction | review | invoice
}


def init_session_state() -> None:
    """Initialisiert den Streamlit-Session-State mit Standardwerten."""
    for key, val in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_document_state() -> None:
    """Setzt alle dokumentbezogenen State-Keys zurück für eine neue Urkunde."""
    st.session_state.parsed_document = None
    st.session_state.extraction_result = None
    st.session_state.final_positions = []
    st.session_state.generated_invoice = None
    st.session_state.generated_audit = None
    st.session_state.auslagen = {"dokumentenpauschale": 0.0, "post_telekom": 0.0, "sonstige": 0.0}
    st.session_state.workflow_step = "upload"
    if "position_editor" in st.session_state:
        del st.session_state["position_editor"]
