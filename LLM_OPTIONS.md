# LLM-Optionen – Notar GNotKG Assistent Cloud

## Unterstützte Cloud-LLM-Provider

Diese Datei ersetzt die frühere `verfuegbare_LLMs.txt`. Die Cloud-Version nutzt ausschließlich Online-LLM-Provider über LiteLLM. Jeder Nutzer benötigt einen eigenen API-Key.

### Mistral (Default)

- `mistral-large-latest` – empfohlen für beste Qualität
- `mistral-medium-latest`
- `mistral-small-latest`

### Anthropic

- `claude-3-5-sonnet-20241022` – empfohlen
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

### xAI

- `grok-3` – empfohlen, falls verfügbar
- `grok-2-1212`

### Moonshot / Kimi

- `moonshot-v1-8k` – empfohlen für kürzere Urkunden
- `moonshot-v1-32k`
- `moonshot-v1-128k`

### DeepSeek

- `deepseek-chat` – empfohlen
- `deepseek-reasoner`

## Konfiguration

Provider und Modell werden in der App-Sidebar ausgewählt. Der API-Key wird lokal verschlüsselt gespeichert. Details zur Einrichtung finden sich in `LLM_PROVIDERS.md`.

## Weiterführende Links

- LiteLLM Provider-Dokumentation: https://docs.litellm.ai/docs/providers
- `LLM_PROVIDERS.md` – Schritt-für-Schritt-Anleitung für API-Keys
