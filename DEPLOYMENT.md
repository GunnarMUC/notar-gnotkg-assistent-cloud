# Deployment & Installation – Notar GNotKG Assistent Cloud

## Voraussetzungen

### Hardware (empfohlen)

- Jeder moderne Rechner mit **≥ 8 GB RAM** (keine GPU nötig, da alles über Cloud-APIs läuft)
- ≥ 2 GB freier Festplattenspeicher

### Software

- **Python 3.12+**
- **uv** (empfohlen) oder **pip**
- Optional: **Tesseract OCR** für gescannte PDFs

### Cloud-Account

- Account bei einem unterstützten Provider (Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek)
- API-Key mit ausreichendem Guthaben

---

## 1. System-Abhängigkeiten (macOS)

```bash
# OCR für gescannte PDFs
brew install tesseract tesseract-lang-deu

# Optional: Pandoc für RTF-Generierung
brew install pandoc
```

**Linux** (Ubuntu/Debian):

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu pandoc
```

---

## 2. Python-Umgebung einrichten

### Mit uv (empfohlen)

```bash
cd notar-gnotkg-assistent-cloud
uv sync
```

### Mit venv + pip

```bash
cd notar-gnotkg-assistent-cloud
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. LLM-Provider-Account einrichten

Wählen Sie einen Provider und erstellen Sie einen API-Key:

| Provider | Anmeldung |
|----------|-----------|
| Mistral | https://console.mistral.ai |
| Anthropic | https://console.anthropic.com |
| xAI | https://console.x.ai |
| Moonshot/Kimi | https://platform.moonshot.cn |
| DeepSeek | https://platform.deepseek.com |

Detaillierte Hinweise finden Sie in [LLM_PROVIDERS.md](LLM_PROVIDERS.md).

---

## 4. App starten

```bash
cd notar-gnotkg-assistent-cloud

# Mit uv:
uv run streamlit run app.py

# Mit venv:
source .venv/bin/activate
streamlit run app.py
```

Die App öffnet sich unter **http://localhost:8501**.

---

## 5. Erster Durchlauf – Kurzanleitung

1. **App starten** (siehe Schritt 4).
2. **Notar-Profil ausfüllen** (automatisch beim ersten Start oder Sidebar).
3. **LLM-Provider konfigurieren**:
   - Sidebar → **LLM-Provider** erweitern.
   - Provider und Modell auswählen.
   - API-Key eingeben.
   - Master-Passwort eingeben und auf **Speichern** klicken.
4. **Beispielurkunde hochladen** (aus `Beispielurkunden/txt/` oder eigene Urkunde).
5. **„Dokument analysieren“** klicken.
6. **Extraktion prüfen** – Positionen bearbeiten/korrigieren.
7. **„Finale Positionen bestätigen“** → Rechnung generieren.
8. **Rechnung + Excel-Log herunterladen**.

---

## 6. API-Key-Verwaltung

- API-Keys werden in `data/provider_keys.json` lokal verschlüsselt gespeichert.
- Die Verschlüsselung nutzt dasselbe Master-Passwort wie das Notar-Profil.
- Keys werden **niemals** im Git-Repository oder in der Cloud gespeichert.
- Um Keys zu laden, Master-Passwort in der Sidebar eingeben und auf **Laden** klicken.

---

## 7. Docker (optional)

Die App kann auch im Docker-Container betrieben werden.

```bash
# Image bauen
docker build -t notar-gnotkg-cloud -f docker/Dockerfile .

# Container starten
docker run -d \
  --name notar-cloud \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/history:/app/history \
  notar-gnotkg-cloud
```

**Hinweis**: Da es sich um eine Cloud-Version handelt, ist kein lokaler Ollama-Dienst nötig. Der Container benötigt lediglich ausgehenden Internetzugang zu den gewählten LLM-Providern.

---

## 8. Verzeichnisstruktur nach Installation

```
notar-gnotkg-assistent-cloud/
├── data/
│   ├── notary_profile.json          # Notar-Stammdaten
│   ├── provider_keys.json           # Verschlüsselte API-Keys
│   ├── notar_app.db                 # SQLite (History, Audit)
│   ├── fee_tables/
│   │   └── v2026_01.json            # Aktuelle Gebührentabelle
│   └── generated_invoices/          # Erstellte Rechnungen
├── history/
│   └── audit_full.jsonl             # Append-Only Audit-Log
└── prompts/
    └── extraction_v1.txt            # Aktueller Extraktions-Prompt
```

---

## 9. Updates

### App-Update

```bash
git pull
uv sync
```

### Fee-Engine-Update

Neue JSON-Tabelle in `data/fee_tables/` ablegen. Die App erkennt neue Versionen und warnt bei veralteten Tabellen. Details siehe `FEE_CALCULATION_LOGIC.md`.

### GNotKG-Aktualitätsprüfung

Die App prüft beim Start automatisch auf `gesetze-im-internet.de`, ob die lokale GNotKG-Version noch aktuell ist. Bei Abweichung erscheint eine Warnung im UI.

---

## 10. Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| **Authentifizierung fehlgeschlagen** | API-Key in der Sidebar prüfen; Key im Provider-Portal erneut erstellen. |
| **Rate-Limit erreicht** | Später erneut versuchen oder anderen Provider wählen. |
| **Modell nicht gefunden** | Modellbezeichnung in der Provider-Dokumentation prüfen. |
| **Kein API-Key hinterlegt** | Sidebar → LLM-Provider → Key eingeben und speichern. |
| **OCR funktioniert nicht** | `tesseract --list-langs` – muss `deu` enthalten; `brew install tesseract-lang-deu` |
| **Streamlit-Port belegt** | `streamlit run app.py --server.port 8502` |
| **GNotKG-Check schlägt fehl** | Kein Internet oder Firewall; App bleibt offline nutzbar |

---

## 11. Sicherheitshinweise

- Die App ist für den **lokalen Einzelplatz-Betrieb** ausgelegt.
- Streamlit läuft standardmäßig nur auf `localhost` (nicht aus dem Netzwerk erreichbar).
- API-Keys und Notar-Profil liegen verschlüsselt im lokalen Dateisystem.
- Urkundeninhalte werden an den gewählten Cloud-Provider übermittelt.

---

**Bei Problemen oder Fragen**: Siehe `README.md`, `LLM_PROVIDERS.md` oder `SECURITY.md`.
