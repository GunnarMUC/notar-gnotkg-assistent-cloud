# Security Policy – Notar GNotKG Assistent Cloud

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in **Notar GNotKG Assistent Cloud**, please report it responsibly.

1. **Do not open a public issue.**
2. Send an e-mail to the maintainer with a detailed description and, if possible, steps to reproduce.
3. We will acknowledge receipt within 5 business days and aim to provide a fix or mitigation within 30 days.

## Security Design

- **Cloud-LLM processing**: Document contents are sent to the external LLM provider chosen by the user. The user is responsible for selecting a provider and API key.
- **Deterministic fee calculation**: All GNotKG-relevant amounts are computed by audited Python code, not by the LLM.
- **Human-in-the-loop**: Every LLM suggestion must be reviewed and confirmed by the notary.
- **API-Key storage**: API keys are stored encrypted locally in `data/provider_keys.json` using the same master password as the notary profile. Keys are never hardcoded, logged, or committed to Git.
- **Sensitive data**: The notary profile is stored in `data/notary_profile.json`. We recommend encrypting the profile with a master password.

## Security Tools

This repository runs the following security checks in CI:

- Gitleaks (secret scanning)
- Semgrep (SAST)
- pip-audit (dependency CVE scanning)
- `ruff` (linting) and `mypy` (type checking)

## Known Limitations

- LLM outputs can hallucinate. Always verify extracted positions before generating an invoice.
- The application is intended for local, single-user deployments on trusted hardware.
- Urkundeninhalte verlassen das Gerät und werden vom gewählten Cloud-Provider verarbeitet. Die datenschutzkonforme Nutzung liegt in der Verantwortung des Nutzers.
