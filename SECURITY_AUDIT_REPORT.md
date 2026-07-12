# Security Audit Report – Notar GNotKG Assistent Cloud

**Datum:** 12. Juli 2026  
**Repository:** [github.com/GunnarMUC/notar-gnotkg-assistent-cloud](https://github.com/GunnarMUC/notar-gnotkg-assistent-cloud)  
**Durchgeführt nach:** `opencode_audit_readiness_instructions.md` (ISO 27001 / SOC 2)  
**Auditor:** Opencode Security Pre-Check Workflow

---

## Executive Summary

Das Projekt „Notar GNotKG Assistent Cloud" wurde einer systematischen Security-Analyse unterzogen. Es wurden **automatisierte Scans** (Gitleaks, Semgrep, pip-audit) und eine **Code-Review** der neuen Cloud-Komponenten durchgeführt. Alle automatisierten Scans zeigen **0 Findings** und alle **77 Unit-Tests** bestehen mit **~91 % Gesamt-Coverage** (CI-Threshold 80 %).

**Wichtige Architekturänderung gegenüber dem Original:** Die Cloud-Version verarbeitet Urkundeninhalte über externe Online-LLM-Provider (Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek). API-Keys werden ausschließlich lokal verschlüsselt gespeichert; keine Keys oder Urkundeninhalte werden im Code, Git oder in der Infrastruktur des Projekts persistiert.

**Gesamtbewertung:** Die Software ist für den beabsichtigten Zweck (Cloud-API-Assistent unter Eigenverantwortung des Nutzers) in einem guten Sicherheitszustand. Die verbleibenden Risiken sind bewusst mit dem Design verbunden (externe Cloud-Verarbeitung) und müssen durch den Nutzer (Notar) mit dem jeweiligen Provider geregelt werden.

---

## 1. Projekt-Scope

| Aspekt | Beschreibung |
|--------|-------------|
| **Sprache** | Python 3.12 |
| **UI** | Streamlit (local browser) |
| **LLM** | Cloud-Provider über LiteLLM (Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek) |
| **API-Key-Speicherung** | Lokal verschlüsselt (`data/provider_keys.json`, Fernet/PBKDF2) |
| **Datenbank** | SQLite + Dateisystem (JSON) |
| **Betrieb** | Lokal, macOS / Linux / Windows / Docker, Single-User |
| **Netzwerk** | Ausgehend zu gewähltem LLM-Provider und `gesetze-im-internet.de` |
| **Docker** | Optional (App im Container, kein Ollama nötig) |
| **Umfang** | 12 `core/`-Module, `app.py`, `ui/`, `docker/`, `prompts/` |

---

## 2. Angewandte Tools & Versionen

| Tool | Version | Zweck | Ergebnis |
|------|---------|-------|----------|
| **Gitleaks** | 8.24.3 | Secrets in Git-History & Files | 0 Leaks |
| **Semgrep** | 1.x | SAST: Python, OWASP Top 10 | 0 Findings |
| **pip-audit** | 2.10.1 | Dependency CVE Scan | Keine bekannten Vulnerabilities |
| **pytest** | 9.1.1 | 77 Unit-Tests | 100 % bestanden, ~91 % Gesamt-Coverage |
| **ruff** | 0.15.21 | Lint & Format | ✅ |
| **mypy** | 2.2.0 | Type-Check | ✅ |

*Hinweis:* Bearer und Trivy wurden nicht erneut ausgeführt, da keine neuen PII-Datenflüsse oder IaC-Änderungen hinzugekommen sind. Empfohlen bleibt eine periodische Wiederholung.

---

## 3. Findings-Übersicht

### Automatisierte Scans

| Tool | Ergebnis |
|------|----------|
| Gitleaks | **0 Leaks** |
| Semgrep | **0 Findings** |
| pip-audit | **0 Vulnerabilities** |
| pytest | **77/77 passed, ~91 % Coverage** |

### Manuelle Code-Review (Cloud-Änderungen)

| # | Schwere | Beschreibung | Status |
|---|---------|-------------|--------|
| C-01 | ✅ Erfüllt | API-Keys niemals im Code oder Git | `provider_key_store.py`, `.gitignore` |
| C-02 | ✅ Erfüllt | API-Keys verschlüsselt lokal gespeichert | `provider_key_store.py`, `profile_crypto.py` |
| C-03 | ✅ Erfüllt | Keine Secrets in Logs | `llm_providers.py` loggt Modell/Provider, nie den Key |
| C-04 | ✅ Erfüllt | Deutliche Cloud-Warnungen in UI | `app.py`, `ui/sidebar.py`, `ui/extraction.py` |
| C-05 | ✅ Erfüllt | Provider-Layer zentralisiert und austauschbar | `core/llm_providers.py` |
| C-06 | ✅ Erfüllt | Keine Hardcoded API-Keys | `.env.example` nur leere Platzhalter |

---

## 4. Umgesetzte Sicherheitsmaßnahmen (Cloud-Version)

### M-01: Verschlüsselte API-Key-Speicherung
- **Dateien:** `core/provider_key_store.py`, `core/profile_crypto.py`
- **Beschreibung:** API-Keys werden mit einem vom Nutzer gewählten Master-Passwort per Fernet/PBKDF2 verschlüsselt in `data/provider_keys.json` abgelegt.
- **Impact:** Selbst bei Zugriff auf das Dateisystem sind die Keys ohne Passwort nicht lesbar.

### M-02: Zentraler Cloud-Provider-Layer
- **Datei:** `core/llm_providers.py`
- **Beschreibung:** Einheitliche Schnittstelle zu allen Providern über LiteLLM; Modell-Namen und API-Key-Variablen werden zentral verwaltet.
- **Impact:** Reduzierte Angriffsfläche, keine verteilten Key-Handlings, einfache Erweiterbarkeit.

### M-03: API-Key-Validierung vor LLM-Aufruf
- **Datei:** `core/llm_extractor.py`
- **Beschreibung:** `extract_from_text` prüft, ob ein Key vorhanden ist (UI oder Environment), und bricht mit klarem Fehler ab, falls nicht.
- **Impact:** Keine unbeabsichtigten Calls ohne Authentifizierung.

### M-04: UI-Warnungen bei Cloud-Nutzung
- **Dateien:** `app.py`, `ui/sidebar.py`, `ui/extraction.py`
- **Beschreibung:** Rote/orange Banner weisen explizit darauf hin, dass Urkundeninhalte den Rechner verlassen.
- **Impact:** Nutzer ist vor jedem Upload informiert.

### M-05: Keine Cloud-Speicherung von Profilen
- **Datei:** `core/config.py`, `ui/helpers.py`
- **Beschreibung:** Notar-Profil und API-Keys bleiben lokal; keine externe Datenbank oder Cloud-Synchronisation.
- **Impact:** Datensouveränität für Profildaten bleibt erhalten.

### M-06: Graceful Error Handling für Provider-Fehler
- **Datei:** `core/llm_providers.py`
- **Beschreibung:** Authentifizierungs-, Rate-Limit- und Verbindungsfehler werden abgefangen und mit nutzerfreundlichen Meldungen weitergegeben.
- **Impact:** Keine internen URLs oder Keys in UI-Fehlermeldungen.

### M-07: CI/CD-Sicherheit
- **Datei:** `.github/workflows/ci.yml`
- **Beschreibung:** Gitleaks wird manuell als Binary ausgeführt, um Probleme mit der GitHub-Action bei Root-Commits zu vermeiden; Semgrep und pip-audit laufen ebenfalls.
- **Impact:** Stabile, reproduzierbare Sicherheits-Scans in der CI.

---

## 5. Compliance Mapping

### ISO 27001 Annex A

| Control | Adressiert durch | Status |
|---------|-----------------|--------|
| A.8.2 Information Classification | Datenminimierung, lokale Speicherung von Profilen/Keys | ✅ |
| A.9.1 Access Control | Lokale Single-User-App, verschlüsselte Key-Speicherung | ⚠️ Akzeptiert |
| A.9.4 System & Application Access | Docker localhost-only, Streamlit nur `localhost` | ✅ |
| A.10.1 Cryptographic Controls | `provider_keys.json` + `notary_profile.json` verschlüsselt (M-01) | ✅ |
| A.12.4 Logging & Monitoring | Keine Keys/PII in Logs, Audit-Trail (Excel) | ✅ |
| A.12.6 Vulnerability Management | pip-audit, Semgrep, Dependency-Updates | ✅ |
| A.14.2 Secure Development | SAST (Semgrep), Code Review, Tests, CI | ✅ |
| A.16 Incident Management | Graceful Degradation, Fehlerbehandlung | ✅ |
| A.18.2 Compliance | DSGVO-Hinweise in UI und Dokumentation | ✅ |

### SOC 2 Trust Services Criteria

| Criterion | Adressiert durch | Status |
|-----------|-----------------|--------|
| CC6.1 Logical Access | Docker non-root, localhost-binding, verschlüsselte Keys | ✅ |
| CC6.3 Access Removal | Single-User, keine Accounts | N/A |
| CC7.1 Detection | Logging (loguru), Audit-Trail (Excel) | ✅ |
| CC7.2 Monitoring | PII-freie Logs, Exception-Handling | ✅ |
| CC8.1 Change Management | Git-Versionierung, Test-Suite, CI | ✅ |

---

## 6. Verbleibende Findings / Residual Risks

| # | Schwere | Beschreibung | Begründung / Mitigation |
|---|---------|-------------|------------------------|
| R-01 | **HIGH** | Urkundeninhalte verlassen das Gerät | Inhärentes Design der Cloud-Version; Nutzer muss eigenen Vertrag/Auftragsverarbeitung mit Provider prüfen. |
| R-02 | **HIGH** | Provider könnte Daten verarbeiten oder speichern | Nur ISO 27001 / SOC 2 zertifizierte Provider wählen; keine sensiblen Daten ohne Notwendigkeit senden. |
| R-03 | **MEDIUM** | API-Key-Verlust bei kompromittiertem Rechner | Key-Datei ist verschlüsselt; zusätzlich FileVault/Verschlüsselung des Systems empfohlen. |
| R-04 | **MEDIUM** | Keine Authentifizierung | Single-User-App; optionaler Streamlit-Passwortschutz dokumentiert. |
| R-05 | **LOW** | Keine Integrity-Checks auf Fee-Tabelle | Test-Suite validiert Werte; JSON-Fallback vorhanden. |
| R-06 | **LOW** | Keine Security Headers | Streamlit-Limitierung; localhost-Betrieb mindert Risiko. |
| R-07 | **LOW** | Kein Dependency-Hash-Pinning | `uv.lock` vorhanden; Verbesserung in CI/CD. |

---

## 7. Empfehlungen für kontinuierliche Sicherheit

### CI/CD Integration (bereits umgesetzt)

Die GitHub Actions führen bereits aus:
- `ruff format`, `ruff check`
- `mypy`
- `pytest` mit Coverage-Threshold
- Gitleaks (manuelles Binary)
- Semgrep
- pip-audit

### Zusätzliche Empfehlungen

- **Dependabot** aktivieren für automatische Dependency-Updates.
- **Regelmäßige API-Key-Rotation** im Provider-Portal dokumentieren.
- **Optionaler Streamlit-Passwortschutz** als Feature für geteilte Rechner.
- **SBOM** (`trivy sbom`) bei Releases generieren.
- **Periodisches Re-Scan** mit Bearer und Trivy, sobald sich Datenflüsse oder Infrastruktur ändern.

---

## 8. Fazit

Die Cloud-Version des „Notar GNotKG Assistenten" wurde erfolgreich auf eine sichere API-Key-Verwaltung und einen einheitlichen Cloud-Provider-Layer umgestellt. Alle automatisierten Scans sind grün, die Testabdeckung liegt bei ~91 % und die wichtigsten Sicherheitsprinzipien (Verschlüsselung, keine Secrets im Code, Warnhinweise, deterministische Berechnung) sind erhalten.

**Status:** Die Software ist für den vorgesehenen Einsatzzweck bereit, sofern der Nutzer die cloud-spezifischen Risiken (Datenverarbeitung durch externe Provider) verantwortungsvoll managed.

---

*Erstellt am 12. Juli 2026 · Security Audit nach opencode_audit_readiness_instructions.md · Gunnar Müller*
