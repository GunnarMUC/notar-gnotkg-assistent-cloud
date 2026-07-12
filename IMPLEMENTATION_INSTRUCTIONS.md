# Implementation Instructions – Notar GNotKG Assistent Cloud

This document is the concrete, developer-oriented guide for building the **cloud-only version** of the Notar GNotKG Assistent. It replaces the previous Ollama/local-LLM implementation with an API-first architecture using external cloud providers (Mistral, Anthropic, xAI, Moonshot/Kimi, DeepSeek) via LiteLLM.

---

## 1. Repository

- **GitHub Repo:** `github.com/GunnarMUC/notar-gnotkg-assistent-cloud`
- **Language:** Python 3.12
- **Package Manager:** `uv`
- **License:** MIT (adjust if required)

---

## 2. Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| UI | Streamlit | Local browser, optional password protection |
| LLM Orchestration | LiteLLM | Unified interface to multiple cloud providers |
| HTTP / API calls | `httpx` (via LiteLLM) | Managed by LiteLLM internally |
| Encryption | `cryptography` (Fernet/PBKDF2) | Same as notary profile encryption |
| Database | SQLite + JSON | Local only |
| Config | `.env` + `core/config.py` | Provider configs, no keys in repo |
| Testing | pytest + coverage | 77 tests, ~91% coverage |
| CI/CD | GitHub Actions | ruff, mypy, pytest, gitleaks, semgrep, pip-audit |

---

## 3. Project Structure

```
notar-gnotkg-assistent-cloud/
├── app.py                          # Streamlit entry point
├── .env.example                    # Empty placeholders only
├── pyproject.toml                  # Dependencies, ruff, pytest, mypy
├── uv.lock                         # Locked dependencies
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── prompts/
│   └── ...                         # LLM prompt templates
├── core/
│   ├── config.py                   # Provider config, default model
│   ├── models.py                   # Pydantic data models
│   ├── llm_providers.py            # NEW: Cloud provider layer (LiteLLM)
│   ├── provider_key_store.py       # NEW: Encrypted API-key storage
│   ├── llm_extractor.py            # Refactored: LLM extraction
│   ├── fee_calculator.py
│   ├── document_parser.py
│   ├── profile_crypto.py
│   ├── notary_profile.py
│   ├── state_manager.py
│   └── document_manager.py
├── ui/
│   ├── sidebar.py                  # Provider selection + API-key input
│   ├── extraction.py
│   ├── state.py
│   ├── helpers.py
│   └── screens.py
└── tests/
    ├── test_llm_providers.py       # NEW
    ├── test_provider_key_store.py  # NEW
    ├── test_llm_extractor.py       # Updated
    └── ...
```

---

## 4. Phase-by-Phase Implementation

### Phase 0: Cleanup

- Remove the `ollama` Python dependency.
- Remove `verfuegbare_LLMs.txt`.
- Delete any Ollama-specific checks or environment variables.

### Phase 1: Add Dependencies

In `pyproject.toml`:

```toml
dependencies = [
    "streamlit>=1.45.0",
    "litellm>=1.72.0",
    "pydantic>=2.10.0",
    "python-dotenv>=1.1.0",
    "loguru>=0.7.0",
    "httpx>=0.28.0",
    "cryptography>=44.0.0",
    "pandas>=2.2.0",
    "sqlalchemy>=2.0.0",
    "openpyxl>=3.1.0",
    "pypdf>=5.1.0",
]
```

Run:

```bash
uv add litellm
uv sync --locked
```

### Phase 2: Implement Cloud Provider Layer

Create `core/llm_providers.py` with:

- A `ProviderConfig` dataclass / enum.
- A mapping of provider names to LiteLLM model identifiers and API-key environment variables.
- A function `get_llm_response(provider, prompt, model, api_key, temperature, max_tokens)` that calls `litellm.completion`.
- Graceful error handling for missing keys, auth failures, rate limits, and network errors.
- Optional `mock_mode` for tests.

Environment variables accepted by LiteLLM for each provider (e.g. `MISTRAL_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY`, `MOONSHOT_API_KEY`, `DEEPSEEK_API_KEY`).

### Phase 3: Implement Encrypted API-Key Storage

Create `core/provider_key_store.py`:

- Load/save `data/provider_keys.json`.
- Encrypt keys with the same master password and `profile_crypto.py` utilities.
- Support retrieving keys by provider name.
- Support deleting / updating keys.

Update `core/config.py`:

- Define `DEFAULT_PROVIDER = "mistral"`.
- Add `PROVIDER_CONFIGS` mapping.
- Add helper to read optional environment API keys.

### Phase 4: Refactor LLM Extraction

Update `core/llm_extractor.py`:

- Replace Ollama calls with calls to `core/llm_providers.get_llm_response`.
- Accept `provider` and `api_key` parameters.
- Validate API key presence (UI or environment) before calling.
- Keep the same prompt assembly and JSON parsing logic.
- Keep retry logic for transient provider errors.

### Phase 5: Refactor UI

Update `ui/sidebar.py`:

- Add a provider selection dropdown.
- Add a password-masked API-key input.
- Add a cloud-warning info box.
- Store the encrypted key via `provider_key_store.py` when the user saves.

Update `ui/state.py`:

- Add session-state keys: `provider`, `api_key`, `api_key_source`.

Update `ui/helpers.py`:

- Add `load_provider_key()`, `save_provider_key()` helpers.
- Ensure keys are encrypted before persistence and decrypted when needed for a request.

Update `app.py`:

- Show a persistent cloud warning at the top.
- Prompt the user to set an API key if none is configured.

Update `ui/extraction.py`:

- Pass the selected provider and API key to `extract_from_text`.
- Display clear error messages for missing/invalid keys.

### Phase 6: Tests

Write `tests/test_llm_providers.py`:

- Test provider configuration lookup.
- Test model name resolution.
- Test missing key detection.
- Test mock response path.
- Test error handling.

Write `tests/test_provider_key_store.py`:

- Test save/load with encryption.
- Test invalid password handling.
- Test missing key file.
- Test key deletion.

Update `tests/test_llm_extractor.py`:

- Replace Ollama mocks with LiteLLM mocks.
- Test provider/API-key parameter flow.
- Test JSON fallback extraction.

Run tests until coverage is ≥ 90%.

### Phase 7: Docker & Deployment

Update `docker/Dockerfile`:

- Remove Ollama installation and service start.
- Keep `uv` / multi-stage build for Python dependencies.
- Expose `8501`.
- Ensure no secrets in image layers.

Update `docker/docker-compose.yml`:

- Remove `ollama` service.
- Mount a local `data/` directory for persistence.

### Phase 8: Documentation

Update or create:

- `README.md` – Cloud usage, API-key setup, provider list.
- `SECURITY.md` – Cloud warning, encrypted keys, data flow.
- `DEPLOYMENT.md` – No Ollama required.
- `TECH_STACK_AND_DEPENDENCIES.md` – Replace Ollama with LiteLLM.
- `ARCHITECTURE.md` – Update data-flow diagram / description.
- `UI_SCREENS_AND_FLOW.md` – Provider selection, API-key screen, cloud warnings.
- `LLM_PROVIDERS.md` – Supported providers and model identifiers.
- `LLM_OPTIONS.md` – Choosing a provider.
- `SECURITY_AUDIT_REPORT.md` – Audit for cloud version.
- `UMSETZUNGSREPORT.md` – Implementation report.
- `FUNCTIONAL_SPECIFICATION.md` – Replace “local LLM” with “cloud LLM”.
- `IMPLEMENTATION_INSTRUCTIONS.md` – This file.

### Phase 9: CI/CD

Ensure `.github/workflows/ci.yml` runs:

- `ruff format --check` and `ruff check`
- `mypy .`
- `pytest` with `--cov` threshold
- Gitleaks (manual binary download to avoid GitHub Action edge cases)
- Semgrep
- pip-audit

Fix any failing steps before merging to `main`.

---

## 5. Environment Variables

All API keys can be provided either via the Streamlit UI (encrypted local storage) or via environment variables. The UI values take precedence over environment variables if present.

```bash
# Example .env (not committed)
MISTRAL_API_KEY=...
ANTHROPIC_API_KEY=...
XAI_API_KEY=...
MOONSHOT_API_KEY=...
DEEPSEEK_API_KEY=...
```

Never commit `.env` or `data/` files.

---

## 6. Quality Gates

Before considering the implementation complete, verify:

- [ ] `uv sync --locked` succeeds
- [ ] `ruff format --check` succeeds
- [ ] `ruff check` succeeds
- [ ] `mypy .` succeeds
- [ ] `pytest` passes (77 tests)
- [ ] Coverage ≥ 80 % (currently ~91 % total / ~85 % core modules)
- [ ] Gitleaks finds 0 secrets
- [ ] Semgrep finds 0 issues
- [ ] pip-audit finds 0 vulnerabilities
- [ ] CI badge is green on `main`

---

## 7. Common Pitfalls

1. **Hardcoding API keys** – Always use the key store or environment variables. Never push keys.
2. **Logging keys** – Ensure `llm_providers.py` logs only provider/model, never the key.
3. **Missing key validation** – `llm_extractor.py` must fail gracefully if no key is available.
4. **LiteLLM fallback** – If a provider fails, return a clear error to the user; do not silently switch providers.
5. **Test isolation** – Mock `litellm.completion` so tests run without real API keys.

---

*Last updated: 12 July 2026*
