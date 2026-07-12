"""UI-Hilfsfunktionen für die Streamlit-App."""

import json

from core.config import get_settings
from core.profile_crypto import (
    ProfileCryptoError,
    decrypt_profile,
    encrypt_profile,
    is_encrypted_profile,
)
from core.provider_key_store import (
    ProviderKeyStoreError,
)
from core.provider_key_store import (
    load_provider_keys as _load_provider_keys,
)
from core.provider_key_store import (
    save_provider_keys as _save_provider_keys,
)

settings = get_settings()


def load_notary_profile(password: str | None = None) -> tuple[dict | None, str | None]:
    """Lädt das Notar-Profil aus der lokalen JSON-Datei.

    Args:
        password: Master-Passwort, falls das Profil verschlüsselt ist.

    Returns:
        Tuple (profil, fehler). Bei Erfolg ist fehler None.
    """
    path = settings.data_dir_path / "notary_profile.json"
    if not path.exists():
        return None, None

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, f"Profil-Datei ist kein gültiges JSON: {e}"
    except OSError as e:
        return None, f"Profil-Datei konnte nicht gelesen werden: {e}"

    if is_encrypted_profile(raw):
        if password is None:
            return None, "Profil ist verschlüsselt. Bitte Master-Passwort eingeben."
        try:
            return decrypt_profile(raw, password), None
        except ProfileCryptoError as e:
            return None, str(e)

    return raw, None


def save_notary_profile(profile: dict, password: str | None = None) -> dict[str, str]:
    """Speichert das Notar-Profil lokal.

    Args:
        profile: Das zu speichernde Profil.
        password: Optional: Master-Passwort für Verschlüsselung.

    Returns:
        Dictionary mit dem gespeicherten Dateiinhalt.
    """
    path = settings.data_dir_path / "notary_profile.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    data = encrypt_profile(profile, password) if password else {**profile, "encrypted": "false"}

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        raise OSError(f"Profil konnte nicht gespeichert werden: {e}") from e
    return data


def load_provider_keys(password: str | None = None) -> tuple[dict[str, str] | None, str | None]:
    """Lädt die gespeicherten API-Keys für Cloud-LLM-Provider.

    Args:
        password: Master-Passwort, falls die Keys verschlüsselt sind.

    Returns:
        Tuple (keys, fehler). Bei Erfolg ist fehler None.
    """
    path = settings.provider_keys_path
    if not path.exists():
        return {}, None

    try:
        return _load_provider_keys(password), None
    except ProviderKeyStoreError as e:
        return None, str(e)


def save_provider_keys(keys: dict[str, str], password: str | None = None) -> None:
    """Speichert die API-Keys für Cloud-LLM-Provider lokal.

    Args:
        keys: Dictionary mit Provider-Namen und API-Keys.
        password: Optional: Master-Passwort für Verschlüsselung.
    """
    _save_provider_keys(keys, password)


def get_provider_key(provider: str, password: str | None = None) -> str | None:
    """Gibt den API-Key für einen bestimmten Provider zurück."""
    keys, _ = load_provider_keys(password)
    if keys is None:
        return None
    return keys.get(provider)
