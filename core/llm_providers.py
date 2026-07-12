"""Einheitlicher LLM-Provider-Layer über LiteLLM (Cloud-Only)."""

from typing import Any

import litellm
from litellm import completion
from loguru import logger

from core.config import get_settings

litellm.suppress_debug_info = True
litellm.set_verbose = False


class Provider:
    """Unterstützte Cloud-LLM-Provider."""

    ANTHROPIC = "anthropic"
    XAI = "xai"
    MOONSHOT = "moonshot"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"


DEFAULT_MODELS: dict[str, str] = {
    Provider.ANTHROPIC: "claude-sonnet-5",
    Provider.XAI: "grok-4.5",
    Provider.MOONSHOT: "kimi-k2.6",
    Provider.MISTRAL: "mistral-medium-latest",
    Provider.DEEPSEEK: "deepseek-v4-pro",
}

API_KEY_ENV_VARS: dict[str, str] = {
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.XAI: "XAI_API_KEY",
    Provider.MOONSHOT: "MOONSHOT_API_KEY",
    Provider.MISTRAL: "MISTRAL_API_KEY",
    Provider.DEEPSEEK: "DEEPSEEK_API_KEY",
}

DISPLAY_NAMES: dict[str, str] = {
    Provider.ANTHROPIC: "Anthropic Claude",
    Provider.XAI: "xAI Grok",
    Provider.MOONSHOT: "Moonshot Kimi",
    Provider.MISTRAL: "Mistral AI",
    Provider.DEEPSEEK: "DeepSeek",
}

SUPPORTED_PROVIDERS: list[str] = list(DEFAULT_MODELS.keys())


def get_default_model(provider: str) -> str:
    """Gibt das Standardmodell für einen Provider zurück."""
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS[Provider.MISTRAL])


def get_display_name(provider: str) -> str:
    """Gibt den Anzeigenamen für einen Provider zurück."""
    return DISPLAY_NAMES.get(provider, provider)


def get_full_model_name(provider: str, model: str | None) -> str:
    """Baut den vollständigen LiteLLM-Modellnamen mit Provider-Prefix."""
    model = model or get_default_model(provider)
    if "/" not in model:
        return f"{provider}/{model}"
    return model


def get_api_key_env_var(provider: str) -> str:
    """Gibt den Namen der Umgebungsvariable für den API-Key zurück."""
    return API_KEY_ENV_VARS.get(provider, f"{provider.upper()}_API_KEY")


def get_api_key_from_env(provider: str) -> str | None:
    """Liest den API-Key für einen Provider aus den Umgebungsvariablen."""
    import os

    env_var = get_api_key_env_var(provider)
    return os.environ.get(env_var) or None


def call_llm(
    messages: list[dict[str, str]],
    provider: str,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    max_retries: int = 3,
) -> str:
    """Führt einen einheitlichen Chat-Completion-Call über LiteLLM aus.

    Args:
        messages: Liste von {"role": ..., "content": ...}-Dictionaries.
        provider: Provider-Name (z. B. "mistral").
        model: Modellname (optional, sonst Default des Providers).
        api_key: API-Key (optional, sonst wird die Umgebung verwendet).
        temperature: Sampling-Temperatur.
        max_tokens: Maximale Token-Ausgabe.
        max_retries: Anzahl Retry-Versuche.

    Returns:
        Roher Text der LLM-Antwort.
    """
    settings = get_settings()
    provider = provider or settings.llm_provider
    full_model = get_full_model_name(provider, model or settings.llm_model)
    temperature = temperature or settings.llm_temperature

    kwargs: dict[str, Any] = {
        "model": full_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "num_retries": max_retries,
        "response_format": {"type": "json_object"},
    }
    if api_key:
        kwargs["api_key"] = api_key

    logger.info(
        f"LLM-Aufruf: Provider={provider}, "
        f"Modell={model or get_default_model(provider)}, "
        f"Textlänge={sum(len(m.get('content', '')) for m in messages)} Zeichen"
    )

    try:
        response = completion(**kwargs)
        content = response.choices[0].message.content
        return content or ""
    except litellm.AuthenticationError as e:
        raise RuntimeError(
            f"Authentifizierung bei {get_display_name(provider)} fehlgeschlagen. "
            "Bitte überprüfen Sie den API-Key in den Einstellungen."
        ) from e
    except litellm.RateLimitError as e:
        raise RuntimeError(
            f"Rate-Limit bei {get_display_name(provider)} erreicht. Bitte später erneut versuchen."
        ) from e
    except litellm.APIConnectionError as e:
        raise RuntimeError(
            f"Verbindung zu {get_display_name(provider)} fehlgeschlagen. "
            "Bitte prüfen Sie Ihre Internetverbindung."
        ) from e
    except litellm.BadRequestError as e:
        raise RuntimeError(f"Ungültige Anfrage an {get_display_name(provider)}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Fehler beim Aufruf von {get_display_name(provider)}: {e}") from e
