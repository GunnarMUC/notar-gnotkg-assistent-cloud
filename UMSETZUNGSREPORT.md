# Umsetzungsreport – Notar GNotKG Assistent Cloud

**Datum:** 12. Juli 2026  
**Projekt:** Notar GNotKG Assistent – Cloud-API-Version  
**Repository:** [github.com/GunnarMUC/notar-gnotkg-assistent-cloud](https://github.com/GunnarMUC/notar-gnotkg-assistent-cloud)  
**Version:** MVP Cloud-Version

---

## 1. Projektziel

Entwicklung einer **Cloud-API-Version** des Notar GNotKG Assistenten, die im Gegensatz zur ursprünglichen lokalen Ollama-Version ausschließlich über externe LLM-Provider per API arbeitet.

| Feature | Status |
|---------|--------|
| Cloud-LLM-Anbindung via LiteLLM | ✅ |
| Mehrere Provider (Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek) | ✅ |
| Verschlüsselte, lokale API-Key-Speicherung pro Nutzer | ✅ |
| Refactoring aller Kernmodule | ✅ |
| Testsuite mit 77 Tests und ~91 % Coverage | ✅ |
| CI/CD mit Gitleaks, Semgrep, pip-audit, ruff, mypy, pytest | ✅ |

---

## 2. Architektur-Änderungen

### 2.1 Neue / Umbenannte Komponenten

| Modul | Zweck | Status |
|-------|-------|--------|
| `core/llm_providers.py` | Zentrale Cloud-Provider-Steuerung (LiteLLM) | ✅ Neu |
| `core/provider_key_store.py` | Verschlüsselte Speicherung der API-Keys | ✅ Neu |
| `core/llm_extractor.py` | Angepasst an Cloud-Provider-Schnittstelle | ✅ Refactored |
| `core/config.py` | Provider-Config und Default-Provider | ✅ Refactored |
| `ui/sidebar.py` | Provider-Auswahl, API-Key-Eingabe, Warnhinweise | ✅ Refactored |
| `ui/state.py` | Session-State für Provider und API-Key | ✅ Refactored |
| `ui/extraction.py` | UI-Integration der Cloud-Extraktion | ✅ Refactored |
| `ui/helpers.py` | Verschlüsselte Persistierung von Provider-Keys | ✅ Refactored |
| `app.py` | Cloud-Warnung, Startbildschirm | ✅ Refactored |

### 2.2 Entfernte / Nicht mehr benötigte Komponenten

| Komponente | Grund |
|-----------|-------|
| `ollama` Python-Dependency | Cloud-Version nutzt ausschließlich externe APIs |
| Ollama-Check in `core/llm_extractor.py` | Nicht mehr relevant |
| `verfuegbare_LLMs.txt` | Ersetzt durch `LLM_PROVIDERS.md` |

---

## 3. LLM-Extraktion (neu)

### Ablauf

1. Nutzer wählt in der Streamlit-Sidebar einen Provider (z. B. Mistral).
2. Nutzer gibt seinen persönlichen API-Key ein oder setzt ihn via `LITELLM_API_KEY` / `MISTRAL_API_KEY` in der Umgebung.
3. Der Key wird lokal verschlüsselt in `data/provider_keys.json` gespeichert.
4. Beim Start einer Extraktion wird der Key aus dem verschlüsselten Store oder der Umgebung geladen.
5. `core/llm_extractor.py` ruft über `core/llm_providers.py` / LiteLLM das gewählte Modell auf.
6. Ergebnis: Strukturierte JSON-Daten (Honorar, Teilung, Verfahrenswert, Rechtsquellen, etc.).

### Sicherheitsmerkmale

- API-Key niemals im Source-Code oder Git.
- Verschlüsselte lokale Speicherung mit dem gleichen Master-Passwort wie das Notar-Profil.
- Keine Persistierung der Urkundeninhalte auf externen Servern (nur Anfrage/Response an Provider).
- Klare UI-Warnung vor Verlassen der Daten.

---

## 4. Test-Status

### Übersicht

| Testbereich | Tests | Status |
|-------------|-------|--------|
| Provider-Verwaltung | `tests/test_llm_providers.py` | ✅ |
| API-Key-Speicherung | `tests/test_provider_key_store.py` | ✅ |
| LLM-Extraktion | `tests/test_llm_extractor.py` | ✅ |
| Datenmodelle | `tests/test_models.py` | ✅ |
| Weitere Kernmodule | `tests/test_*.py` | ✅ |
| **Gesamt** | **77 Tests** | **✅ 100 % bestanden** |

### Coverage

Aktuelle Abdeckung gemessen mit `pytest tests/ -v --cov --cov-fail-under=80`:

| Modul | Coverage |
|-------|----------|
| `core/llm_extractor.py` | 94 % |
| `core/llm_providers.py` | 85 % |
| `core/fee_engine.py` | 88 % |
| `core/invoice_generator.py` | 94 % |
| `core/profile_crypto.py` | 100 % |
| `core/models.py` | 100 % |
| `core/provider_key_store.py` | 73 % |
| `core/document_parser.py` | 49 % |
| **Gesamt (inkl. Tests)** | **~91 %** |
| **CI-Threshold** | **80 %** |

---

## 5. CI/CD Status

| Check | Tool | Status |
|-------|------|--------|
| Formatting | ruff format | ✅ |
| Linting | ruff check | ✅ |
| Type-Check | mypy | ✅ |
| Unit Tests | pytest + coverage | ✅ 77/77 |
| Secret Scan | Gitleaks (manual binary) | ✅ 0 Leaks |
| SAST | Semgrep | ✅ 0 Findings |
| Dependency Audit | pip-audit | ✅ 0 Vulnerabilities |

**Badge:** `CI` ist grün.

---

## 6. Bekannte Limitierungen

1. **Cloud-Abhängigkeit:** Für jede Nutzung ist Internet-Zugang und ein gültiger API-Key erforderlich.
2. **Datenschutz:** Urkundeninhalte werden an externe Provider übermittelt. Der Nutzer ist für die Einhaltung von DSGVO/AVV selbst verantwortlich.
3. **Single-User:** Keine Mehrbenutzer-Verwaltung oder Rollenkonzept.
4. **Keine automatische Rotation:** API-Keys müssen vom Nutzer manuell im Provider-Portal rotiert werden.
5. **Kein Offlineszenario:** Ohne Internet oder Provider-Ausfall ist keine LLM-Extraktion möglich.

---

## 7. Deployment

### Ohne Docker

```bash
uv sync --locked
uv run streamlit run app.py
```

### Mit Docker

```bash
docker build -t notar-gnotkg-cloud .
docker run -p 8501:8501 notar-gnotkg-cloud
```

**Hinweis:** Es ist kein Ollama-Server mehr erforderlich. Die App benötigt lediglich ausgehenden HTTPS-Zugriff zum gewählten Provider.

---

## 8. Zusammenfassung

Die Cloud-Version des Notar GNotKG Assistenten ist vollständig auf externe LLM-APIs umgestellt. Die Architektur ist modular, der Provider-Layer zentralisiert und die API-Key-Sicherheit durch lokale Verschlüsselung gewährleistet. Alle Tests bestehen, die CI ist grün und die wichtigsten Dokumente wurden aktualisiert.

**Nächste Schritte (optional):**

- Unterstützung weiterer Provider (z. B. Azure OpenAI, Google Gemini) über `llm_providers.py` ergänzen.
- Abrechnung pro Nutzer / API-Usage-Tracking erweitern.
- Optionalen Streamlit-Passwortschutz für geteilte Workstations implementieren.
- Dependabot für automatische Sicherheits-Updates aktivieren.

---

*Erstellt am 12. Juli 2026 · Gunnar Müller*
