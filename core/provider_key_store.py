"""Verschlüsselte Speicherung der API-Keys für Cloud-LLM-Provider."""

import json
from pathlib import Path

from core.config import get_settings
from core.profile_crypto import (
    ProfileCryptoError,
    decrypt_profile,
    encrypt_profile,
    is_encrypted_profile,
)


class ProviderKeyStoreError(ValueError):
    """Fehler beim Zugriff auf den API-Key-Speicher."""


def _provider_keys_path() -> Path:
    return get_settings().provider_keys_path


def load_provider_keys(password: str | None = None) -> dict[str, str]:
    """Lädt alle gespeicherten Provider-API-Keys.

    Args:
        password: Master-Passwort, falls die Keys verschlüsselt gespeichert sind.

    Returns:
        Dictionary mit Provider-Namen als Keys und API-Keys als Values.
    """
    path = _provider_keys_path()
    if not path.exists():
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ProviderKeyStoreError(f"Provider-Keys-Datei ist kein gültiges JSON: {e}") from e

    if is_encrypted_profile(raw):
        if password is None:
            raise ProviderKeyStoreError(
                "API-Keys sind verschlüsselt. Bitte Master-Passwort eingeben."
            )
        try:
            decrypted = decrypt_profile(raw, password)
        except ProfileCryptoError as e:
            raise ProviderKeyStoreError(str(e)) from e
        return _validate_keys(decrypted)

    return _validate_keys(raw)


def _validate_keys(data: dict) -> dict[str, str]:
    """Stellt sicher, dass nur string-basierte Provider-Keys zurückgegeben werden."""
    return {str(k): str(v) for k, v in data.items() if isinstance(v, str) and v}


def save_provider_keys(keys: dict[str, str], password: str | None = None) -> None:
    """Speichert alle Provider-API-Keys verschlüsselt oder als Klartext.

    Args:
        keys: Dictionary mit Provider-Namen als Keys und API-Keys als Values.
        password: Master-Passwort für die Verschlüsselung. Ohne Passwort wird
                 die Datei unverschlüsselt gespeichert (nicht empfohlen).
    """
    path = _provider_keys_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    cleaned = _validate_keys(keys)
    data = encrypt_profile(cleaned, password) if password else {"encrypted": "false", **cleaned}

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def update_provider_key(provider: str, api_key: str, password: str | None = None) -> None:
    """Aktualisiert den API-Key eines einzelnen Providers ohne andere zu löschen.

    Args:
        provider: Name des Providers (z. B. "mistral").
        api_key: Der neue API-Key.
        password: Master-Passwort für die Entschlüsselung/Verschlüsselung.
    """
    keys = load_provider_keys(password) if password else _load_unencrypted_or_empty()
    keys[provider] = api_key.strip()
    save_provider_keys(keys, password)


def _load_unencrypted_or_empty() -> dict[str, str]:
    path = _provider_keys_path()
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if is_encrypted_profile(raw):
            return {}
        return _validate_keys(raw)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def get_provider_key(provider: str, password: str | None = None) -> str | None:
    """Gibt den API-Key für einen bestimmten Provider zurück."""
    keys = load_provider_keys(password)
    return keys.get(provider)


def has_provider_key(provider: str, password: str | None = None) -> bool:
    """Prüft, ob für einen Provider ein API-Key vorhanden ist."""
    return bool(get_provider_key(provider, password))
