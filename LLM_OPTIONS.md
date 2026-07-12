# LLM-Optionen – Notar GNotKG Assistent Cloud

## Unterstützte Cloud-LLM-Provider

Diese Datei ersetzt die frühere `verfuegbare_LLMs.txt`. Die Cloud-Version nutzt ausschließlich Online-LLM-Provider über LiteLLM. Jeder Nutzer benötigt einen eigenen API-Key.

Die Empfehlungen sind nach aktuellem Stand (Juli 2026) gewählt und orientieren sich an den jeweiligen Provider-Frontiermodellen. LiteLLM fügt den Provider-Präfix automatisch hinzu, z. B. wird `mistral-medium-latest` intern zu `mistral/mistral-medium-latest`.

### Mistral (Default)

- `mistral-medium-latest` – **Empfohlen** (Mistral Medium 3.5, frontier multimodal, sehr gute Agent-/Coding-Leistung)
- `mistral-large-3` – State-of-the-art Open-Weight-Allzweckmodell (v25.12)
- `magistral-medium-2506` – Reasoning-Modell mit Funktionsaufrufen, gut für komplexe Extraktionen
- Alternativ für schnelle/kostengünstige Fälle: `mistral-small-latest`

### Anthropic

- `claude-sonnet-5` – **Empfohlen** (beste Balance aus Qualität, Geschwindigkeit und Kosten, Juni 2026)
- `claude-opus-4-8` – Höchste Qualität für besonders komplexe oder anspruchsvolle Fälle
- `claude-haiku-4-5` – Sehr schnell und günstig, aber leistungsschwächer

### xAI

- `grok-4.5` – **Empfohlen** (intelligentestes Grok-Modell, 500k Kontext)
- `grok-4.3` – Großer 1M-Kontext für sehr lange Urkunden
- `grok-4.20-0309-reasoning` – Reasoning-Variante für schwierige Extraktionen
- Alternativ LiteLLM-konform: `grok-4-1-fast-reasoning` (2M Kontext)

### Moonshot / Kimi

- `kimi-k2.6` – **Empfohlen** (intelligentestes Kimi-Modell, 256k Kontext)
- `kimi-k2.7-code` – Stärkste Coding-Leistung, 256k Kontext (falls über API verfügbar)
- `kimi-k2.5` – Bewährt, gute Vision-Unterstützung, 256k Kontext
- Für preiswerte Langtexte: `moonshot-v1-128k` (ältere Generation)

### DeepSeek

- `deepseek-v4-pro` – **Empfohlen** (beste Qualität, 1M Kontext)
- `deepseek-v4-flash` – Schnell & günstig, 1M Kontext, inkl. Thinking-Mode
- `deepseek-reasoner` – Reasoning-Modell (wird am 2026-07-24 deprecated; Ersatz: `deepseek-v4-flash` mit Thinking)

## Konfiguration

Provider und Modell werden in der App-Sidebar ausgewählt. Der API-Key wird lokal verschlüsselt gespeichert. Details zur Einrichtung finden sich in `LLM_PROVIDERS.md`.

## Hinweise zur Auswahl

- Für die beste Extraktionsqualität wählen Sie das jeweils erste empfohlene Modell.
- `-latest`-Aliases werden automatisch auf die aktuelle stabile Version aufgelöst.
- Sie können jeden anderen Modellnamen verwenden, den der Provider über seine API anbietet.

## Weiterführende Links

- LiteLLM Provider-Dokumentation: https://docs.litellm.ai/docs/providers
- `LLM_PROVIDERS.md` – Schritt-für-Schritt-Anleitung für API-Keys

*Stand: Juli 2026*
