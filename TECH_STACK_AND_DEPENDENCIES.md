# Tech-Stack & Abhängigkeiten – Notar GNotKG Assistent Cloud

## Primärer Tech-Stack

| Bereich | Technologie | Begründung / Alternativen | Version / Hinweis |
|---------|-------------|---------------------------|-------------------|
| **UI / Frontend** | Streamlit | Einfach, interaktiv, Python-only, gute Komponenten für Tabellen & Downloads | Aktuellste stabile Version |
| **LLM Runtime** | LiteLLM | Einheitliche Schnittstelle für Mistral, Anthropic, xAI, Moonshot, DeepSeek | ≥ 1.65.0 |
| **LLM Modelle** | Cloud-Provider-Modelle | Mistral, Claude, Grok, Kimi, DeepSeek | Je nach Verfügbarkeit |
| **Backend Language** | Python 3.12+ | Ökosystem, LLM-Integration, Dokumenten-Libs | 3.12 empfohlen |
| **Package Manager** | `uv` (empfohlen) oder `pip` | Schnell, moderne Lockfiles | - |
| **Dokumenten-Parsing** | `pymupdf` (fitz) + `pytesseract` | Gute PDF-Qualität + OCR-Fallback | + `tesseract-ocr-deu` |
| **Strukturierte Ausgabe** | Pydantic v2 + JSON-Parsing | Typsicher, Validierung, Retry-Logik | - |
| **Office-Generierung** | `python-docx` | Professionelle DOCX-Erstellung | - |
| **RTF** | Pandoc (System) oder Fallback | Gute Konvertierung von Markdown/HTML → RTF | Optional, System-Dependency |
| **Excel** | `pandas` + `openpyxl` | Traceability-Logs | - |
| **Templates** | Jinja2 | Flexible Rechnungs-Templates | - |
| **Datenbank** | SQLite (via `sqlalchemy`) | Einfach, lokal, ausreichend für History | Datei-basiert |
| **Web-Requests** | `httpx` | Moderner Async-Client für GNotKG-Check | - |
| **Logging / Audit** | `loguru` | Strukturiertes Logging | - |
| **Konfiguration** | `pydantic-settings` | Typsichere Config | - |
| **Testing** | `pytest` + `pytest-mock` | Standard für Python | - |
| **Verschlüsselung** | `cryptography` (Fernet/PBKDF2) | Master-Passwort-basierte Verschlüsselung von Profil und API-Keys | - |

## Docker (optional)

- **Base Image**: `python:3.12-slim` oder `python:3.12-bookworm`
- **Ziel**: App im Container
- **Hinweis**: Kein Ollama nötig, aber ausgehender Internetzugriff zu den gewählten LLM-Providern erforderlich.
- `docker-compose.yml` mit Volume-Mounts für `data/`, `history/`

## System-Abhängigkeiten (macOS)

```bash
# OCR
brew install tesseract tesseract-lang-deu

# Optional für RTF
brew install pandoc
```

## Python Dependencies

```toml
[project]
dependencies = [
    "streamlit>=1.38,<2.0",
    "litellm>=1.65.0",
    "pydantic>=2.8",
    "pydantic-settings>=2.4",
    "pymupdf>=1.24",
    "pytesseract>=0.3.10",
    "python-docx>=1.1",
    "pandas>=2.2",
    "openpyxl>=3.1",
    "jinja2>=3.1",
    "httpx>=0.27",
    "loguru>=0.7",
    "sqlalchemy>=2.0",
    "cryptography>=42.0",
]
```

## Unterstützte Provider (Stand 2026)

| Provider | Modellbeispiel | API-Key-Variable |
|----------|----------------|------------------|
| Mistral | `mistral-large-latest` | `MISTRAL_API_KEY` |
| Anthropic | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| xAI | `grok-3` | `XAI_API_KEY` |
| Moonshot/Kimi | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |
| DeepSeek | `deepseek-chat` | `DEEPSEEK_API_KEY` |

Siehe `LLM_PROVIDERS.md` für Details zur Einrichtung.

## Warum dieser Stack?

- **Flexibilität**: Einheitliche LiteLLM-Schnittstelle für mehrere Cloud-Provider
- **Minimale Komplexität** → schnelle Umsetzung eines MVP
- **Gute Developer Experience** (Streamlit, uv, Pydantic)
- **Rechtliche Sicherheit** durch deterministische Berechnung
- **Wartbarkeit** bei zukünftigen GNotKG-Änderungen
- **Sicherheit**: API-Keys und Profil werden lokal verschlüsselt

---

**Nächster Schritt**: Lies `DEPLOYMENT.md` für die Installationsanleitung und `LLM_PROVIDERS.md` für die Provider-Setup.
