# LLM-Provider – Notar GNotKG Assistent Cloud

## Übersicht

Die Cloud-Version unterstützt fünf Online-LLM-Provider über die einheitliche [LiteLLM](https://docs.litellm.ai/)-Schnittstelle.  
Jeder Nutzer muss bei seinem gewählten Provider einen eigenen Account anlegen und einen API-Key erstellen. Der Key wird **ausschließlich lokal verschlüsselt** gespeichert.

## Wichtige Hinweise

- **Urkundeninhalte verlassen Ihr Gerät** – nur der API-Key-Datei-Besitzer kann steuern, wo sie verarbeitet werden.
- **Jeder Nutzer zahlt selbst** – die Abrechnung läuft direkt über den jeweiligen Provider.
- **Kein API-Key im Code oder Git** – Keys werden in `data/provider_keys.json` mit Ihrem Master-Passwort verschlüsselt.
- **Haftung** – Die datenschutzkonforme Nutzung liegt in Ihrer Verantwortung.

## Unterstützte Provider

### Mistral (Default)

- **LiteLLM-Provider**: `mistral`
- **Default-Modell**: `mistral-large-latest`
- **API-Key**: `MISTRAL_API_KEY`
- **Anmeldung**: https://console.mistral.ai
- **Dokumentation**: https://docs.mistral.ai/
- **Hinweis**: Gute Deutschkenntnisse, günstiges Preismodell, EU-Standort verfügbar.

### Anthropic

- **LiteLLM-Provider**: `anthropic`
- **Default-Modell**: `claude-3-5-sonnet-20241022`
- **API-Key**: `ANTHROPIC_API_KEY`
- **Anmeldung**: https://console.anthropic.com
- **Dokumentation**: https://docs.anthropic.com
- **Hinweis**: Sehr gute Reasoning-Qualität, allgemein höherer Preis.

### xAI

- **LiteLLM-Provider**: `xai`
- **Default-Modell**: `grok-3`
- **API-Key**: `XAI_API_KEY`
- **Anmeldung**: https://console.x.ai
- **Dokumentation**: https://docs.x.ai
- **Hinweis**: Verfügbarkeit und Modelle können sich schnell ändern.

### Moonshot / Kimi

- **LiteLLM-Provider**: `moonshot`
- **Default-Modell**: `moonshot-v1-8k`
- **API-Key**: `MOONSHOT_API_KEY`
- **Anmeldung**: https://platform.moonshot.cn
- **Dokumentation**: https://platform.moonshot.cn/docs
- **Hinweis**: Starke Performance bei deutschen Texten; Account- und Abrechnung oft in China.

### DeepSeek

- **LiteLLM-Provider**: `deepseek`
- **Default-Modell**: `deepseek-chat`
- **API-Key**: `DEEPSEEK_API_KEY`
- **Anmeldung**: https://platform.deepseek.com
- **Dokumentation**: https://platform.deepseek.com/docs
- **Hinweis**: Günstig, aber beachten Sie den Server-Standort und Datenschutzbestimmungen.

## API-Key in der App hinterlegen

1. App starten (`streamlit run app.py`).
2. In der Sidebar auf **LLM-Provider** erweitern.
3. Provider und Modell auswählen.
4. API-Key in das Passwort-Feld eingeben.
5. Master-Passwort eingeben (gleiches wie für das Notar-Profil).
6. Auf **Speichern** klicken.

Bei jedem Start können Sie die gespeicherten Keys mit dem Master-Passwort über **Laden** entschlüsseln.

## Optional: API-Key über `.env`

Für Entwickler oder Power-User kann ein Key auch über die Umgebung bereitgestellt werden. Erstellen Sie eine `.env`-Datei im Projekt-Root:

```env
LLM_PROVIDER=mistral
MISTRAL_API_KEY=Ihr-API-Key
```

Die UI-gespeicherten Keys haben Vorrang, falls beides gesetzt ist. Die `.env`-Datei darf niemals in Git committet werden (siehe `.gitignore`).

## Fehlerbehebung

| Problem | Lösung |
|---------|--------|
| **Authentifizierung fehlgeschlagen** | API-Key in der Sidebar prüfen; Key im Provider-Portal erneut erstellen. |
| **Rate-Limit erreicht** | Später erneut versuchen oder anderen Provider wählen. |
| **Modell nicht gefunden** | Modellbezeichnung im Provider-Dokumentation prüfen. |
| **Kein API-Key hinterlegt** | Sidebar → LLM-Provider → Key eingeben und speichern. |
| **Passwort falsch** | Master-Passwort prüfen; es ist dasselbe wie für das Notar-Profil. |

## Weitere Informationen

- LiteLLM Provider-Dokumentation: https://docs.litellm.ai/docs/providers
- Sicherheitshinweise: [SECURITY.md](SECURITY.md)
- Deployment-Anleitung: [DEPLOYMENT.md](DEPLOYMENT.md)
