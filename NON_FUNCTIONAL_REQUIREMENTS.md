# Nicht-funktionale Anforderungen – Notar GNotKG Assistent Cloud

## 1. Performance & Effizienz

### NFR-P01: App-Startzeit
- App-Start (Streamlit) inklusive GNotKG-Versions-Check: **< 5 Sekunden** bei normaler Internetverbindung
- Ohne Internetverbindung (Offline): **< 2 Sekunden** (Timeout des GNotKG-Checks wird abgefangen)

### NFR-P02: Dokument-Parsing
- PDF-Parsing (Text-Modus): **< 3 Sekunden** für Dokumente bis 50 Seiten
- OCR-Fallback (gescanntes PDF): **< 30 Sekunden** für 10 Seiten
- Fortschrittsanzeige bei OCR-Verarbeitung

### NFR-P03: LLM-Extraktion
- Extraktion einer Urkunde (bis 10.000 Tokens): **< 60 Sekunden** über den gewählten Cloud-Provider (abhängig von Netzwerk und Provider)
- Bei > 30 Sekunden: Spinner mit Statusmeldung
- Abbruch-Möglichkeit für den Nutzer

### NFR-P04: Gebührenberechnung (Fee Engine)
- Berechnung einer Position: **< 50 ms** (sollte instantan wirken)
- Neuberechnung der gesamten Tabelle nach Edit: **< 200 ms**

### NFR-P05: Rechnungsgenerierung
- DOCX-Generierung (1–10 Positionen): **< 2 Sekunden**
- Excel-Traceability-Log: **< 3 Sekunden**

---

## 2. Zuverlässigkeit & Fehlertoleranz

### NFR-R01: Graceful Degradation
- Bei fehlendem oder ungültigem API-Key: Klare Fehlermeldung mit Hinweis zur Key-Eingabe in der Sidebar
- Bei Rate-Limit oder API-Fehler des Providers: Benutzerfreundliche Meldung und Vorschlag, später erneut zu versuchen
- Bei fehlgeschlagenem GNotKG-Check: Warnung, aber App bleibt nutzbar (Offline-Modus)
- Bei PDF-Parsing-Fehler: Fallback auf manuelle Texteingabe

### NFR-R02: Datenintegrität
- SQLite mit WAL-Mode für Crash-Sicherheit
- Erstellte Rechnungen und Logs sofort auf Platte persistieren (nicht nur im Speicher)
- Keine Datenverluste bei App-Absturz (Streamlit-Session-States sind flüchtig – finalisierte Daten immer persistieren)

### NFR-R03: Eingabevalidierung
- Alle Benutzereingaben validieren vor Speicherung/Weitergabe
- Pflichtfelder im Notar-Profil hervorheben
- Geschäftswerte: Akzeptiere nur positive Zahlen, sinnvolle Ober- und Untergrenzen (1 € – 500.000.000 €)
- Datei-Upload: Größenbeschränkung auf 50 MB (typische Urkunden sind < 5 MB)

---

## 3. Sicherheit

### NFR-S01: Netzwerkverbindungen
- **Ausgehende Verbindungen** nur zu:
  - Dem gewählten Cloud-LLM-Provider (Mistral, Anthropic, xAI, Moonshot, DeepSeek)
  - `gesetze-im-internet.de` (optionaler GNotKG-Check, einmalig beim Start)
- Keine Telemetrie, kein Crash-Reporting, kein Tracking
- Docker-Container: Ausgehender Internetzugriff zu den gewählten Providern erforderlich

### NFR-S02: Authentifizierung & Zugriff
- **Keine Benutzer-Authentifizierung** erforderlich (lokale Single-User-App)
- Streamlit-App läuft standardmäßig nur auf `localhost:8501`
- Optionaler Passwort-Schutz für Streamlit (empfohlen in DEPLOYMENT.md dokumentieren)

### NFR-S03: Datensicherheit
- Alle Daten (Urkunden, Profile, Rechnungen, Logs, API-Keys) ausschließlich im lokalen Dateisystem
- API-Keys werden verschlüsselt in `data/provider_keys.json` gespeichert
- Keine Cloud-Speicherung von Keys oder Profilen, aber Urkundeninhalte werden zur Verarbeitung an den gewählten Provider übermittelt
- SQLite-Datenbank im App-Datenverzeichnis (`data/`)
- Gitignore: `data/history/`, `data/notar_profile.json`, `data/provider_keys.json`, `data/notar_app.db`

### NFR-S04: Secrets Management
- Keine hartcodierten Secrets, API-Keys oder Tokens im Code
- Notar-Profil (IBAN, Steuernummer) in `data/notary_profile.json` – Zugriff nur lokal
- API-Keys in `data/provider_keys.json` – verschlüsselt mit demselben Master-Passwort wie das Notar-Profil
- `.env`-Datei für optionale Konfiguration (LLM-Provider, API-Keys) – nicht ins Git-Repo

---

## 4. Datenschutz & DSGVO

### NFR-D01: Datenminimierung
- App speichert nur das absolut Notwendige:
  - Notar-Profil (einmalig)
  - Generierte Rechnungen (Archiv)
  - Audit-Logs (Abrechnungszwecke)
  - Verschlüsselte API-Keys
- Keine Speicherung ganzer Urkundentexte über die aktuelle Session hinaus (konfigurierbar)

### NFR-D02: Datenhoheit
- Notar hat volle Kontrolle über alle gespeicherten Daten
- Export-Funktion für alle gespeicherten Rechnungen (Massendownload)
- Lösch-Funktion für Historie (einzelne Einträge oder alles)

### NFR-D03: Verarbeitungsverzeichnis
- Klarer Hinweis in Dokumentation, welche Daten wie verarbeitet werden
- Urkundeninhalte verlassen das lokale Gerät zur Verarbeitung durch den gewählten Cloud-LLM-Provider
- Der Nutzer ist für die datenschutzkonforme Nutzung und ggf. einen Auftragsverarbeitungsvertrag mit dem Provider verantwortlich

---

## 5. Usability & Benutzerfreundlichkeit

### NFR-U01: Zielgruppengerechte UI
- Alle UI-Texte auf Deutsch
- Klare, juristisch bekannte Begriffe (GNotKG, KV-Nr., Geschäftswert)
- Minimaler Trainingsaufwand: Notar soll ohne Handbuch arbeiten können

### NFR-U02: Fehlervermeidung & Assistenz
- Undo-Funktion in editierbarer Tabelle (oder Warnung vor unbeabsichtigten Änderungen)
- Plausibilitäts-Checks mit Warnhinweisen (z. B. „Geschäftswert 45.000.000 € – entspricht das tatsächlich Ihrer Urkunde?“)
- Tooltipps zu KV-Nummern und Berechnungsgrundlagen

### NFR-U03: Barrierefreiheit (Grundlegend)
- Ausreichende Schriftgrößen (≥ 14px)
- Kontrastreiche Farbgestaltung (KI-Vorschlag vs. bestätigt)
- Tastatur-Navigation in editierbarer Tabelle (via Streamlit/HTML)

### NFR-U04: Feedback & Status
- Eindeutige Status-Indikatoren:
  - Grün: Berechnung erfolgreich, bestätigt
  - Gelb: KI-Vorschlag, ungeprüft, Warnung
  - Rot: Fehler, kritische Warnung
- Fortschrittsbalken bei längeren Operationen (OCR, LLM-Extraktion)

---

## 6. Kompatibilität & Plattformen

### NFR-C01: Primärplattform macOS
- Entwickelt und getestet auf macOS 14+ (Sonoma) und 15+ (Sequoia) auf Apple Silicon (M1–M4)
- Streamlit-Betrieb im Standard-Browser (Safari, Chrome, Firefox)

### NFR-C02: Sekundärplattformen
- Linux (Ubuntu 22.04+, Debian 12+): Grundsätzlich lauffähig
- Windows: Lauffähig mit WSL2
- Docker: Primär für Linux/macOS

### NFR-C03: Browser
- Safari 17+, Chrome 120+, Firefox 120+ (aktuelle Versionen)
- Streamlit unterstützt alle gängigen Browser nativ

---

## 7. Wartbarkeit & Erweiterbarkeit

### NFR-M01: Modularer Code
- Klare Trennung in `core/`-Module mit definierten Schnittstellen
- Fee-Engine und Prompts unabhängig aktualisierbar
- Jede Komponente einzeln testbar (Unit-Tests)

### NFR-M02: Versionierung
- Fee-Engine: Versioniert mit GNotKG-Stand-Datum (z. B. `v2026_01`)
- Prompts: Versioniert in `prompts/extraction_vX.txt`
- App-Version in `pyproject.toml` oder `__init__.py`
- Jede generierte Rechnung enthält die verwendeten Versionen (Fee-Engine + LLM-Provider + Modell + Prompt)

### NFR-M03: Konfigurierbarkeit
- Alle Pfade und Parameter über `pydantic-settings` + `.env` oder JSON konfigurierbar
- Keine hartcodierten Pfade (außer Defaults)

### NFR-M04: Abhängigkeiten
- Minimale Anzahl an externen Abhängigkeiten
- Alle Abhängigkeiten mit konkreten Versionen in `pyproject.toml` oder `requirements.txt` gepinnt
- Regelmäßiger Dependency-Update-Check (Dependabot/Renovate empfohlen)

---

## 8. Testbarkeit & Qualitätssicherung

### NFR-T01: Unit-Tests
- Fee-Engine: 100 % Testabdeckung der Berechnungslogik (kritischstes Modul)
- Ausreichende Tests mit echten Praxis-Beispielen (aus Beispielurkunden und notar.de)

### NFR-T02: Integrationstests
- End-to-End-Test: Urkunde (TXT) → Extraktion → Fee-Engine → Rechnung
- Mit verschiedenen Urkundentypen aus `Beispielurkunden/`

### NFR-T03: Testdaten
- 15 Beispielurkunden in `Beispielurkunden/txt/` als Test-Fixtures nutzbar
- Anonymisierte, realistische Daten aus Grundstückskauf und Testament

---

## 9. Dokumentation

### NFR-DOC01: Code-Dokumentation
- Alle öffentlichen Funktionen mit Docstrings (auf Python-Ebene)
- Deutsche Kommentare für business-relevante Logik

### NFR-DOC02: Nutzerdokumentation
- Vollständige Installations- und Nutzungsanleitung (`DEPLOYMENT.md`)
- Provider-spezifische Anleitung (`LLM_PROVIDERS.md`)
- Erklärungen zu GNotKG-Grundlagen in der App (Tooltipps, Hilfe-Button)
- Disclaimer rechtssicher und prominent

---

## 10. Auditierbarkeit & Compliance

### NFR-A01: Traceability
- Jeder Berechnungsschritt muss nachvollziehbar sein (siehe `FR-06` in `FUNCTIONAL_SPECIFICATION.md`)
- Excel-Log enthält: Quelle → KV-Nr → Geschäftswert → Berechnungsformel → Endergebnis
- Bei manuellen Overrides: Vorher/Nachher dokumentiert

### NFR-A02: Revisionssicherheit
- Append-Only-Log (`audit_full.jsonl`) im Dateisystem
- Jeder Audit-Eintrag mit Timestamp, Version und Nutzer-Aktion
- Löschungen nur durch explizite Nutzeraktion, nicht automatisch

### NFR-A03: GNotKG-Konformität
- Umsetzung der gesetzlichen Anforderungen an die Kostenberechnung (§ 19 GNotKG)
- Rechtsbehelfsbelehrung in jeder Rechnung (§ 7a GNotKG)
- Disclaimer zur Verantwortung des Notars (§ 17 BNotO)
