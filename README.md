# Notar GNotKG Assistent – Cloud

> **Cloud-only API-Version: GNotKG-Honorarrechnung mit wählbaren Online-LLM-Providern.**
> Jeder Nutzer verwendet seinen eigenen API-Key und trägt Datenschutz sowie Kosten selbst.

[![CI](https://github.com/GunnarMUC/notar-gnotkg-assistent-cloud/actions/workflows/ci.yml/badge.svg)](https://github.com/GunnarMUC/notar-gnotkg-assistent-cloud/actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](tests/)
[![Security Audit](https://img.shields.io/badge/security%20audit-passed-brightgreen)](SECURITY_AUDIT_REPORT.md)
[![Semgrep](https://img.shields.io/badge/semgrep-0%20findings-brightgreen)](SECURITY_AUDIT_REPORT.md)
[![Gitleaks](https://img.shields.io/badge/gitleaks-0%20leaks-brightgreen)](SECURITY_AUDIT_REPORT.md)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

---

## Hinweis zur lokalen Original-Version

Dies ist die **Cloud-API-Version** des [Notar GNotKG Assistenten](https://github.com/GunnarMUC/notar-gnotkg-assistent).  
Wer ausschließlich lokal und DSGVO-konform arbeiten möchte, verwendet das Original-Repository.

---

## Das Problem

Honorarrechnungen nach dem Gerichts- und Notarkostengesetz (GNotKG) sind komplex, fehleranfällig und zeitaufwändig. Gebührenbeträge müssen juristisch exakt sein. Cloud-LLMs können die Extraktion beschleunigen, setzen voraus, dass sensible Urkundeninhalte den Rechner verlassen.

## Die Lösung

Ein **Cloud-Assistent**, der Urkunden mit einem vom Nutzer gewählten Online-LLM versteht, Geschäftswerte und KV-Nummern vorschlägt und Gebühren **deterministisch exakt** berechnet. Die KI entscheidet niemals über Beträge – das übernimmt eine auditierte Python-Engine.

---

## Innovation & Alleinstellungsmerkmale

| Innovation | Warum es zählt |
|------------|----------------|
| **Wählbare Cloud-Provider** | Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek über einheitliche LiteLLM-Schnittstelle. |
| **Eigenverantwortliche API-Keys** | Jeder Nutzer speichert seinen eigenen API-Key lokal verschlüsselt und wird direkt vom Provider abgerechnet. |
| **Deterministische Engine** | KI extrahiert Fakten, Python berechnet Gebühren. Keine Halluzinationen bei Beträgen. |
| **Human-in-the-Loop** | Jede KI-Vorschlagsposition muss vom Notar geprüft und bestätigt werden. |
| **Verschlüsselte Key-Speicherung** | API-Keys werden mit dem Master-Passwort (Fernet/PBKDF2) lokal verschlüsselt. |
| **Revisionssicheres Excel-Log** | Jede Rechnung erhält ein Traceability-Log: Wert → Paragraph → Gebühr. |
| **Versionierte Gebührentabellen** | GNotKG-Tabelle B und KV-Definitionen als strukturierte JSON-Dateien zukunftssicher hinterlegt. |

---

## Schnellstart

```bash
# 1. Account bei einem unterstützten Provider anlegen und API-Key erstellen
#    Siehe LLM_PROVIDERS.md

# 2. Projekt einrichten
git clone https://github.com/GunnarMUC/notar-gnotkg-assistent-cloud.git
cd notar-gnotkg-assistent-cloud
uv sync

# 3. App starten
uv run streamlit run app.py
```

Danach unter `http://localhost:8501` öffnen.  
Im ersten Schritt in der Sidebar den Provider wählen, API-Key eingeben und speichern.

---

## Kernfunktionen

- **Urkunden-Upload**: PDF (mit OCR), DOCX, RTF, TXT
- **KI-Extraktion**: Geschäftswerte, Beteiligte, KV-Nummern per Cloud-LLM
- **Interaktive Prüfung**: Editierbare Positionstabelle mit Confidence-Score
- **Deterministische Berechnung**: GNotKG-Anlage 2 (Tabelle B) exakt nach dem Gesetz
- **Rechnungserstellung**: DOCX, RTF oder TXT
- **Audit-Trail**: Automatisches Excel-Traceability-Log pro Rechnung
- **GNotKG-Aktualitäts-Check**: Abgleich mit gesetze-im-internet.de beim Start
- **Notar-Profil**: Einmalig einrichten, optional verschlüsselt speichern

---

## Architektur

```text
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│  Urkunde    │────▶│  Cloud-LLM        │────▶│  Vorschlag     │
│  (PDF/...)  │     │  (Mistral/...)    │     │  Positionen    │
└─────────────┘     └──────────────────┘     └────────────────┘
                                                       │
                                                       ▼
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│  Rechnung   │◀────│  Fee Engine       │◀────│  Notar prüft  │
│  + Excel-Log│     │  (deterministisch)│     │  & bestätigt   │
└─────────────┘     └──────────────────┘     └────────────────┘
```

Trennung von KI und Berechnung ist das zentrale Sicherheitsprinzip: das LLM liest und schlägt vor, die Engine rechnet.

---

## Sicherheit & Compliance

- **API-Keys niemals im Code oder Git**: Keys werden lokal verschlüsselt in `data/provider_keys.json` gespeichert.
- **Jeder Nutzer sein eigener Verantwortlicher**: Jeder trägt seinen eigenen API-Key ein und wird direkt vom Provider abgerechnet.
- **SAST & Dependency Audit**: Semgrep und pip-audit in der CI.
- **Verschlüsselung**: AES-verschlüsselte Speicherung des Notar-Profils und der API-Keys mit demselben Master-Passwort.
- **Haftungsausschluss**: Urkundeninhalte verlassen das Gerät. Die datenschutzkonforme Nutzung liegt in der Verantwortung des Notars.

Details in [LLM_PROVIDERS.md](LLM_PROVIDERS.md), [SECURITY.md](SECURITY.md) und [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Projektstruktur

```text
notar-gnotkg-assistent-cloud/
├── app.py                  # Dünner Streamlit-Einstieg
├── core/                   # Geschäftslogik
│   ├── fee_engine.py       # Deterministische GNotKG-Berechnung
│   ├── document_parser.py  # PDF/DOCX/RTF/TXT + OCR
│   ├── llm_extractor.py    # LLM-Extraktion über LiteLLM
│   ├── llm_providers.py    # Cloud-Provider-Layer
│   ├── provider_key_store.py # Verschlüsselte API-Key-Speicherung
│   ├── invoice_generator.py
│   ├── excel_logger.py
│   ├── gnotkg_checker.py
│   └── profile_crypto.py   # Profilverschlüsselung
├── ui/                     # Streamlit-UI-Komponenten
├── data/fee_tables/        # Versionierte JSON-Gebührentabellen
├── prompts/                # System-Prompts + Few-Shots
├── tests/                  # 77 Tests, ~90 % Coverage
└── SECURITY_AUDIT_REPORT.md
```

---

## Unterstützte Provider

| Provider | Default-Modell | API-Key-Umgebungsvariable |
|----------|----------------|---------------------------|
| Mistral | `mistral-large-latest` | `MISTRAL_API_KEY` |
| Anthropic | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| xAI | `grok-3` | `XAI_API_KEY` |
| Moonshot/Kimi | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |
| DeepSeek | `deepseek-chat` | `DEEPSEEK_API_KEY` |

Siehe [LLM_PROVIDERS.md](LLM_PROVIDERS.md) für Anleitungen zum Erstellen der API-Keys.

---

## Roadmap

- [x] Cloud-Only-Version mit LiteLLM
- [x] Verschlüsselte, nutzereigene API-Key-Speicherung
- [x] Unterstützung für Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek
- [x] CI/CD mit Qualitätssicherung, SAST & Dependency-Audit
- [ ] Weitere KV-Nummern aus dem Kostenverzeichnis
- [ ] Rechnungs-Templates (HTML/Jinja2)
- [ ] SQLite-basierte Historie + Volltextsuche
- [ ] Beta-Test bei Notarkanzleien

---

## Lizenz & Haftung

MIT License. Die Software ist ein Assistenztool. Die alleinige Verantwortung für die Richtigkeit und die Einhaltung des GNotKG liegt stets beim Notar (§ 17 BNotO).  
Die Cloud-Version übermittelt Urkundeninhalte an externe Dienste. Nutzung erfolgt auf eigene Verantwortung.

---

**Erstellt für**: Deutsche Notare, die Cloud-LLMs unter Eigenverantwortung nutzen möchten.
