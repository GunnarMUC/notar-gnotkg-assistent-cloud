"""Tests für den LLM-Provider-Layer."""

import json

import pytest
from pytest_mock import MockerFixture

from core.llm_providers import (
    Provider,
    call_llm,
    get_api_key_env_var,
    get_default_model,
    get_display_name,
    get_full_model_name,
)


class TestProviderHelpers:
    def test_default_model(self):
        assert get_default_model(Provider.MISTRAL) == "mistral-large-latest"
        assert get_default_model(Provider.ANTHROPIC) == "claude-3-5-sonnet-20241022"

    def test_full_model_name_adds_prefix(self):
        assert get_full_model_name(Provider.MISTRAL, "custom") == "mistral/custom"

    def test_full_model_name_keeps_existing_prefix(self):
        assert get_full_model_name(Provider.MISTRAL, "mistral/custom") == "mistral/custom"

    def test_display_name(self):
        assert get_display_name(Provider.ANTHROPIC) == "Anthropic Claude"

    def test_api_key_env_var(self):
        assert get_api_key_env_var(Provider.DEEPSEEK) == "DEEPSEEK_API_KEY"

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("MISTRAL_API_KEY", "env-key")
        from core.llm_providers import get_api_key_from_env

        assert get_api_key_from_env(Provider.MISTRAL) == "env-key"


class TestCallLlm:
    def test_successful_call(self, mocker: MockerFixture):
        payload = {"answer": "42"}
        message = type("Message", (), {"content": json.dumps(payload)})()
        choice = type("Choice", (), {"message": message})()
        response = type("Response", (), {"choices": [choice]})()

        mock_completion = mocker.patch("core.llm_providers.completion", return_value=response)

        result = call_llm(
            messages=[{"role": "user", "content": "Hallo"}],
            provider=Provider.MISTRAL,
            api_key="test-key",
        )

        assert json.loads(result) == payload
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args.kwargs
        assert call_kwargs["model"] == "mistral/mistral-large-latest"
        assert call_kwargs["api_key"] == "test-key"

    def test_auth_error(self, mocker: MockerFixture):
        import litellm

        mocker.patch(
            "core.llm_providers.completion",
            side_effect=litellm.AuthenticationError(
                "Invalid key",
                llm_provider="mistral",
                model="mistral/mistral-large-latest",
            ),
        )

        with pytest.raises(RuntimeError, match="Authentifizierung"):
            call_llm(messages=[{"role": "user", "content": "Hallo"}], provider=Provider.MISTRAL)
