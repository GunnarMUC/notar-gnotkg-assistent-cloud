"""Tests für den verschlüsselten API-Key-Speicher."""

import pytest

from core.provider_key_store import (
    ProviderKeyStoreError,
    get_provider_key,
    has_provider_key,
    load_provider_keys,
    save_provider_keys,
    update_provider_key,
)


class TestProviderKeyStore:
    def test_roundtrip_encrypted(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DATA_DIR", str(tmp_path))
        # Settings cache muss zurückgesetzt werden, damit DATA_DIR greift
        from core.config import get_settings

        get_settings.cache_clear()
        monkeypatch.setattr(
            "core.config.Settings.provider_keys_path",
            property(lambda self: tmp_path / "provider_keys.json"),
        )

        keys = {"mistral": "mistral-key-123", "anthropic": "anthropic-key-456"}
        save_provider_keys(keys, password="master-password")

        loaded = load_provider_keys(password="master-password")
        assert loaded == keys

    def test_wrong_password(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.config.Settings.provider_keys_path",
            property(lambda self: tmp_path / "provider_keys.json"),
        )

        save_provider_keys({"mistral": "secret"}, password="correct")
        with pytest.raises(ProviderKeyStoreError):
            load_provider_keys(password="wrong")

    def test_update_single_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.config.Settings.provider_keys_path",
            property(lambda self: tmp_path / "provider_keys.json"),
        )

        save_provider_keys({"mistral": "old"}, password="pw")
        update_provider_key("anthropic", "new", password="pw")

        loaded = load_provider_keys(password="pw")
        assert loaded["mistral"] == "old"
        assert loaded["anthropic"] == "new"

    def test_get_and_has_provider_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.config.Settings.provider_keys_path",
            property(lambda self: tmp_path / "provider_keys.json"),
        )

        save_provider_keys({"mistral": "key"}, password="pw")
        assert get_provider_key("mistral", password="pw") == "key"
        assert has_provider_key("mistral", password="pw")
        assert get_provider_key("anthropic", password="pw") is None
        assert not has_provider_key("anthropic", password="pw")

    def test_missing_file_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.config.Settings.provider_keys_path",
            property(lambda self: tmp_path / "provider_keys.json"),
        )

        assert load_provider_keys() == {}
