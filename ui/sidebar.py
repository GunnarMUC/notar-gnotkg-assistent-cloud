"""Sidebar-Komponenten der Streamlit-App."""

import streamlit as st

from core.config import get_settings
from core.llm_providers import (
    SUPPORTED_PROVIDERS,
    Provider,
    get_default_model,
    get_display_name,
)
from ui.helpers import (
    load_notary_profile,
    load_provider_keys,
    save_notary_profile,
    save_provider_keys,
)

settings = get_settings()

# Curated Modelle pro Provider – können vom Nutzer überschrieben werden.
_CURATED_MODELS: dict[str, list[str]] = {
    Provider.MISTRAL: ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
    Provider.ANTHROPIC: [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ],
    Provider.XAI: ["grok-3", "grok-2-1212"],
    Provider.MOONSHOT: ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    Provider.DEEPSEEK: ["deepseek-chat", "deepseek-reasoner"],
}


def render_sidebar() -> None:
    """Rendert die gesamte Sidebar."""
    with st.sidebar:
        st.header("⚙️ Einstellungen")

        _render_cloud_warning()
        st.divider()
        _render_profile_section()
        st.divider()
        _render_provider_section()
        st.divider()
        _render_gnotkg_status_section()
        st.divider()
        st.caption("Notar GNotKG Assistent Cloud v0.1.0")
        st.caption("API-Keys werden lokal verschlüsselt gespeichert.")


def _render_cloud_warning() -> None:
    st.error(
        "⚠️ Cloud-LLM aktiviert: Urkundeninhalte verlassen Ihr Gerät. "
        "Jeder Nutzer benötigt seinen eigenen API-Key und trägt die Datenschutz- "
        "und Kostenverantwortung selbst."
    )


def _render_profile_section() -> None:
    expanded = st.session_state.notary_profile is None

    with st.expander("👤 Notar-Profil", expanded=expanded):
        if st.session_state.notary_profile is None:
            password = st.text_input(
                "Master-Passwort (falls Profil verschlüsselt)",
                type="password",
                key="profile_load_password",
                help="Leer lassen, wenn das Profil unverschlüsselt ist.",
            )
            if st.button("🔓 Profil laden"):
                profile, error = load_notary_profile(password or None)
                if error:
                    st.error(error)
                else:
                    st.session_state.notary_profile = profile
                    st.success("Profil geladen" if profile else "Kein Profil vorhanden")
                    st.rerun()
            return

        profile = st.session_state.notary_profile or {}
        col1, col2 = st.columns(2)
        name = col1.text_input("Name", value=profile.get("name", ""))
        firm_name = col2.text_input("Kanzlei", value=profile.get("firm_name", ""))
        address = st.text_area("Adresse", value=profile.get("address", ""))
        col3, col4 = st.columns(2)
        phone = col3.text_input("Telefon", value=profile.get("phone", ""))
        email = col4.text_input("E-Mail", value=profile.get("email", ""))
        col5, col6 = st.columns(2)
        bank_name = col5.text_input("Bank", value=profile.get("bank_name", ""))
        iban = col6.text_input("IBAN", value=profile.get("iban", ""))
        bic = st.text_input("BIC", value=profile.get("bic", ""))
        tax_number = st.text_input("Steuernummer", value=profile.get("tax_number", ""))
        vat_id = st.text_input("USt-ID", value=profile.get("vat_id", ""))

        st.divider()
        password = st.text_input(
            "Master-Passwort für Verschlüsselung",
            type="password",
            key="profile_save_password",
            help="Mindestens 8 Zeichen empfohlen. Ohne Passwort wird das Profil unverschlüsselt gespeichert.",
        )
        password_confirm = st.text_input(
            "Passwort wiederholen", type="password", key="profile_save_password_confirm"
        )

        if st.button("💾 Profil speichern"):
            if password and password != password_confirm:
                st.error("Passwörter stimmen nicht überein.")
                return

            new_profile = {
                "name": name,
                "firm_name": firm_name,
                "address": address,
                "phone": phone,
                "email": email,
                "bank_name": bank_name,
                "iban": iban,
                "bic": bic,
                "tax_number": tax_number,
                "vat_id": vat_id,
            }
            save_notary_profile(new_profile, password or None)
            st.session_state.notary_profile = new_profile
            if password:
                st.success("Profil verschlüsselt gespeichert!")
            else:
                st.warning(
                    "Profil unverschlüsselt gespeichert. Bitte aus Sicherheitsgründen ein Passwort setzen."
                )


def _render_provider_section() -> None:
    with st.expander("🧠 LLM-Provider", expanded=False):
        provider = st.selectbox(
            "Provider",
            options=SUPPORTED_PROVIDERS,
            format_func=get_display_name,
            index=(
                SUPPORTED_PROVIDERS.index(st.session_state.llm_provider)
                if st.session_state.llm_provider in SUPPORTED_PROVIDERS
                else 0
            ),
        )
        if st.session_state.get("_last_provider") != provider:
            st.session_state.llm_model = get_default_model(provider)
        st.session_state.llm_provider = provider
        st.session_state["_last_provider"] = provider

        models = _CURATED_MODELS.get(provider, [get_default_model(provider)])
        current_model = st.session_state.llm_model
        if current_model not in models:
            models = [current_model] + models
        selected_model = st.selectbox(
            "Modell",
            options=models,
            index=models.index(current_model) if current_model in models else 0,
            key=f"{provider}_model_select",
        )
        custom_model = st.text_input(
            "Eigenes Modell (optional, überschreibt Auswahl)",
            value="",
            key=f"{provider}_custom_model",
            help="Leer lassen, um die Auswahl zu verwenden.",
        )
        st.session_state.llm_model = custom_model.strip() or selected_model

        st.divider()
        st.write("**API-Key**")
        master_password = st.text_input(
            "Master-Passwort (zum Entschlüsseln/Speichern)",
            type="password",
            key="provider_master_password",
            help="Gleiches Passwort wie für das Notar-Profil.",
        )
        api_key_input = st.text_input(
            f"{get_display_name(provider)} API-Key",
            type="password",
            key=f"{provider}_api_key",
            help="Wird lokal verschlüsselt gespeichert, nie in der Cloud oder im Repo.",
        )

        provider_keys = st.session_state.get("provider_keys", {})
        if provider in provider_keys:
            st.info(f"API-Key für {get_display_name(provider)} ist im Session-State vorhanden.")

        col1, col2 = st.columns(2)
        if col1.button("🔓 Laden", key="provider_key_load"):
            keys, error = load_provider_keys(master_password or None)
            if error:
                st.error(error)
            else:
                st.session_state.provider_keys = keys or {}
                st.success("API-Keys geladen")
                st.rerun()
        if col2.button("💾 Speichern", key="provider_key_save"):
            keys_to_save = dict(provider_keys)
            if api_key_input:
                keys_to_save[provider] = api_key_input.strip()
            try:
                save_provider_keys(keys_to_save, master_password or None)
                st.session_state.provider_keys = keys_to_save
                st.success(f"API-Key für {get_display_name(provider)} gespeichert")
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")


def _render_gnotkg_status_section() -> None:
    with st.expander("📜 GNotKG-Status", expanded=False):
        status = st.session_state.gnotkg_status
        if status and status.is_current:
            st.success("✅ GNotKG aktuell")
        elif status and not status.is_current:
            st.warning(f"⚠️ GNotKG veraltet – Aktueller Stand: {status.remote_version}")
        else:
            st.info("ℹ️ Noch nicht geprüft")
