# UI Screens & User Flow – Notar GNotKG Assistent Cloud (Streamlit)

## Gesamter User Flow (MVP)

```
Start App
   │
   ▼
[Sidebar] Notar-Profil + LLM-Provider-Config + GNotKG-Status (grün/gelb/rot)
   │
   ▼
[Hauptbereich] Upload-Bereich (Drag & Drop)
   │
   ▼
Nach Upload → Button "Dokument analysieren"
   │
   ▼
Extraktion läuft (Spinner + Fortschritt) über den gewählten Cloud-Provider
   │
   ▼
Ergebnis-Screen:
   ┌───────────────────────────────┬──────────────────────────────┐
   │ Original-Urkunde (Vorschau /  │ Editierbare Positionen-Tabelle│
   │ "Datei öffnen")               │ (st.data_editor)             │
   │                               │                              │
   │                               │ + Button "Neue Position"     │
   │                               │ + Button "Neu berechnen"     │
   └───────────────────────────────┴──────────────────────────────┘

   Unten: Auslagen-Eingabe + Live-Summe (netto / brutto)

   Button: "Finale Positionen bestätigen"  (Pflicht-Checkbox + Hinweis)
   │
   ▼
Vorschau der Honorarrechnung (HTML-ähnlich oder DOCX-Preview)
   │
   ▼
Auswahl Ausgabeformat (DOCX / RTF / TXT) + "Rechnung + Excel-Log erzeugen"
   │
   ▼
Download-Buttons + Erfolgsmeldung + Link zur Historie
```

## Wichtige Streamlit-Komponenten & Best Practices

- `st.sidebar` für globale Einstellungen, Status und LLM-Provider-Konfiguration
- `st.file_uploader` mit `type=["pdf", "docx", "rtf", "txt"]`
- `st.data_editor` für die zentrale editierbare Tabelle (mit `column_config` für schöne Darstellung)
- `st.columns([2, 3])` für Original vs. Tabelle
- `st.success`, `st.warning`, `st.error` für klare Rückmeldungen
- `st.download_button` für alle generierten Dateien
- Session State Keys: `parsed_document`, `extraction_result`, `final_positions`, `generated_invoice`, `llm_provider`, `llm_model`, `provider_keys` etc.

## Empfohlene visuelle Gestaltung

- Klare Trennung: **KI-Vorschlag** (hellblau/grau) vs. **Final bestätigt** (grün)
- Bei Overrides: Gelbe Markierung + Tooltip mit Begründung
- Deutlicher roter Disclaimer-Bereich auf jeder generierten Rechnung und im Extraktions-Tab
- Deutliche Cloud-Warnungen in Sidebar und Extraktion (Urkundeninhalte verlassen das Gerät)
- Fortschrittsanzeige bei LLM-Aufrufen und bei längeren Operationen

---

**Ziel der UI**: So einfach wie möglich, aber mit maximaler Transparenz, Kontrolle und Warnung vor Cloud-Nutzung für den Notar.