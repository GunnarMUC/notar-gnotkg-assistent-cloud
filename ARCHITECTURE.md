# Architektur – Notar GNotKG Assistent Cloud

## Überblick (High-Level)

Die Cloud-Version folgt derselben modularen Architektur wie das Original, ersetzt jedoch den lokalen Ollama-Client durch einen einheitlichen Cloud-LLM-Provider-Layer über LiteLLM.

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                     │
│  Upload → Vorschau → Editierbare Tabelle → Vorschau Rechnung    │
│  + Notar-Profil + LLM-Provider-Config + Historie                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌──────────────────┐
│ Document      │     │ LLM Extractor   │     │ Fee Engine       │
│ Parser        │────▶│ (LiteLLM)       │────▶│ (deterministisch)│
│ (PDF/OCR/...) │     │                 │     │                  │
└───────────────┘     └─────────────────┘     └────────┬─────────┘
                                                       │
        ┌──────────────────────────────────────────────┼──────────┐
        ▼                                              ▼          ▼
┌──────────────────┐                          ┌────────────────┐  │
│ Invoice          │                          │ Excel Logger   │  │
│ Generator        │                          │ (Traceability) │  │
│ (DOCX/RTF/TXT)   │                          └────────────────┘  │
└──────────────────┘                                              │
                                                                  │
                    ┌─────────────────────────────────────────────┘
                    ▼
            ┌───────────────┐
            │ Local Storage │
            │ (SQLite + FS) │
            └───────────────┘
```

## Komponenten im Detail

### 1. Document Parser (`core/document_parser.py`)
- Unterstützt: PDF (Text + Layout), DOCX, RTF, TXT
- Fallback-OCR mit `pytesseract` + deutschem Sprachpaket für gescannte Dokumente
- Ausgabe: Strukturierter Text + Metadaten (Seitenanzahl, Extraktionsqualität)

### 2. LLM Provider Layer (`core/llm_providers.py`)
- Einheitliche Schnittstelle über LiteLLM
- Unterstützt: Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek
- Verwaltet Provider-Prefixe, Default-Modelle und API-Key-Umgebungsvariablen
- Liefert rohe LLM-Antwort an `llm_extractor.py`

### 3. LLM Extractor (`core/llm_extractor.py`)
- Ruft `core.llm_providers.call_llm()` auf
- Validiert API-Key vor dem Call
- Structured Output via Pydantic-Modelle (JSON Mode + Validation + Retry)
- Liefert:
  - Erkannte Tatbestände / KV-Nummern-Vorschläge
  - Extrahierte Geschäftswerte mit Quellenangabe
  - Beteiligte Personen
  - Confidence / Unsicherheits-Flags
- **Kein direkter Aufruf der Fee-Engine** – nur Vorschläge

### 4. Provider Key Store (`core/provider_key_store.py`)
- Verschlüsselte Speicherung der API-Keys in `data/provider_keys.json`
- Nutzt dasselbe Master-Passwort wie das Notar-Profil
- Unterstützt Laden, Speichern und Aktualisieren einzelner Keys

### 5. Fee Engine (`core/fee_engine.py`) – **Kritischste Komponente**
- **Rein deterministisch** (kein LLM)
- Implementiert Werttabellen, KV-Definitionen, Kombinationsregeln
- Versioniert (z. B. `FeeEngineV2026_01`)
- Gibt für jede Position exakten Betrag + Begründung zurück

### 6. Invoice Generator (`core/invoice_generator.py`)
- Erzeugt professionelle Honorarrechnung
- Formate: DOCX (primär), RTF, TXT
- Verwendet Jinja2-Templates + `python-docx`

### 7. Excel Logger (`core/excel_logger.py`)
- Traceability pro Rechnung
- Enthält: Quelle, KV-Nr, Geschäftswert, LLM-Provider, Modell, Timestamp, Overrides

### 8. GNotKG Checker (`core/gnotkg_checker.py`)
- Beim App-Start: HTTP-Request an `https://www.gesetze-im-internet.de/gnotkg/`
- Vergleich mit lokaler Version
- Bei Abweichung: Warnung + Hinweis auf manuelles Update

### 9. UI Layer (Streamlit)
- Sidebar mit Provider-Auswahl, Modell-Auswahl und API-Key-Eingabe
- Deutliche Cloud-Warnungen in Sidebar und Extraktions-Tab
- Interaktive Tabs für Upload, Extraktion, Prüfung, Rechnung

## Datenfluss (typischer Use-Case)

1. Notar lädt Urkunde hoch
2. Parser → strukturierter Text
3. LLM Extractor → strukturierte Vorschläge (Pydantic) via Cloud-Provider
4. UI zeigt Vorschläge in editierbarer Tabelle
5. Notar prüft, korrigiert, ergänzt Auslagen
6. Bei jeder Änderung → Fee Engine recalculates
7. Notar bestätigt finale Positionen
8. Invoice Generator erzeugt Dokument(e)
9. Excel Logger schreibt Audit-Eintrag
10. Dateien stehen zum Download bereit + werden archiviert

## Design-Prinzipien

- **Human-in-the-Loop by Design**: Keine vollautomatische Rechnungserstellung
- **Deterministisch wo rechtlich relevant**: Gebührenbeträge niemals vom LLM
- **Auditierbarkeit first**: Jeder Schritt nachvollziehbar
- **Lean & Maintainable**: Wenige Abhängigkeiten, klare Module
- **Privacy by Design**: API-Keys lokal verschlüsselt; keine Cloud-Speicherung von Profilen/Keys
- **Erweiterbar**: Neue Provider können in `core/llm_providers.py` hinzugefügt werden

## Technische Schnittstellen

- Cloud-LLM-Provider APIs (über LiteLLM)
- Lokales Dateisystem + SQLite
- Optional: Pandoc für RTF-Konvertierung (System-Tool)

## Skalierbarkeit & Zukunft

Die Architektur ist bewusst für **Einzelnotar / kleine Kanzlei** ausgelegt.  
Spätere Erweiterungen (weitere Provider, Kosten-Tracking, Fallback-Ketten) sind modular möglich, ohne die Kernprinzipien zu verletzen.

---

**Nächste Schritte für die Umsetzung**: Siehe `DEPLOYMENT.md` und `LLM_PROVIDERS.md`.
