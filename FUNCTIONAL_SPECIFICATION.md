# Functional Specification – Notar GNotKG Assistent Cloud

**Version:** 1.0 Cloud  
**Date:** 12 July 2026  
**Repository:** [github.com/GunnarMUC/notar-gnotkg-assistent-cloud](https://github.com/GunnarMUC/notar-gnotkg-assistent-cloud)

This document specifies the functional requirements for the **cloud-only version** of the Notar GNotKG Assistent. The original local Ollama-based LLM has been replaced by external cloud providers accessed via LiteLLM.

---

## 1. System Overview

The system is a single-user Streamlit desktop/web application that helps German notaries assess notarial fees and document types under the GNotKG.

Key change from the original version: the LLM is **not** running locally. Instead, the app sends relevant document text to a user-selected cloud LLM provider through an encrypted API call and receives structured data for downstream processing.

---

## 2. Functional Requirements

### FR-01 Notary Profile Management

The user shall create a single notary profile with:
- Name
- Notary district
- Fee zone (for optional fee correction)
- Optional: VAT inclusion preference
- A master password for encryption

The profile shall be encrypted locally and stored in `data/notary_profile.json`.

### FR-02 LLM Provider Selection

The user shall select a cloud LLM provider from a dropdown:
- Mistral (default)
- Anthropic
- xAI
- Moonshot / Kimi
- DeepSeek

The app shall display the selected provider clearly in the sidebar and extraction screen.

### FR-03 API-Key Configuration

The user shall provide a personal API key for the selected provider. The key shall be entered via a password-masked input field and stored locally encrypted (`data/provider_keys.json`). The key shall never be sent to the GitHub repository or any server other than the selected LLM provider.

Alternatively, the user may provide the key via an environment variable (e.g. `MISTRAL_API_KEY`) as documented in `.env.example`.

### FR-04 Cloud Warning

Before every extraction, the app shall display a clear warning that the document content will be transmitted to the selected external provider and that the user is responsible for compliance with data-protection and professional-secrecy obligations.

### FR-05 Document Upload

The user shall upload one or more documents (PDF, images, text) via the Streamlit interface. The app shall parse the text and display a preview of the extracted content.

### FR-06 LLM Extraction

Given the document text and the selected provider, the app shall call the provider API via LiteLLM and prompt the model to extract:
- Verfahrenswert (procedure value)
- Document type (e.g., Kaufvertrag, Schenkung, Grundschuld)
- Fee-relevant flags (e.g., Anzahl der Vertragsparteien, mehrere Grundstücke)
- Rechtsquellen / GNotKG sections
- Suggested fee calculation steps

The app shall return the extracted data as a structured JSON object compatible with the existing Pydantic models.

### FR-07 Fee Calculation

The app shall calculate the notarial fee based on the extracted data and the notary profile using the GNotKG fee tables. The calculation shall be deterministic and reproducible.

### FR-08 Result Review and Export

The user shall review the extraction result, edit values if necessary, and export the final assessment as:
- Excel (audit-ready)
- PDF summary (optional)
- JSON (optional)

### FR-09 Audit Trail

For every extraction, the app shall record:
- Timestamp
- Selected provider
- Model name
- Document filename (without content)
- Final calculated fee
- User corrections

No API key or document content shall be stored in the audit log.

### FR-10 Offline Limitation

If no internet connection or no valid API key is available, the app shall disable extraction and show an actionable error message.

---

## 3. Non-Functional Requirements (Summary)

- **Security:** API keys encrypted locally; no secrets in Git.
- **Privacy:** Document content leaves the device only via TLS to the selected provider; provider choice is user responsibility.
- **Reliability:** All code paths have unit tests; target coverage ≥ 90%.
- **Usability:** Streamlit UI with German labels, clear warnings, and step-by-step guidance.
- **Maintainability:** Provider layer centralized in `core/llm_providers.py`.

---

## 4. Out of Scope

- Local LLM execution (Ollama, llama.cpp, etc.).
- Multi-user authentication or role management.
- Cloud storage of profiles or documents.
- Automatic billing or usage tracking by the app.
- Training or fine-tuning of models.

---

## 5. Acceptance Criteria

- [ ] User can select a provider and enter an API key.
- [ ] Key is stored encrypted and survives app restart (with correct master password).
- [ ] Extraction succeeds with a valid key for at least the default provider (Mistral).
- [ ] Fee calculation returns deterministic results.
- [ ] All 77 tests pass and CI is green.
- [ ] Gitleaks finds no secrets.
- [ ] Cloud warning is shown before every extraction.

---

*Last updated: 12 July 2026*
