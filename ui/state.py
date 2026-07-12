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
