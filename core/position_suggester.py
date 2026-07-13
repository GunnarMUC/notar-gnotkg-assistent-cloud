"""Vorschläge für fehlende GNotKG-Positionen basierend auf dem Dokumententyp."""

from __future__ import annotations

from typing import Any

from core.gnotkg_catalog import load_gnotkg_catalog
from core.models import ExtractedPosition

# Erwartete KV-Positionen pro Dokumententyp (Schlüsselwörter müssen im Dokumententyp enthalten sein)
DOCUMENT_TYPE_EXPECTATIONS: dict[str, list[str]] = {
    "kauf": ["21200", "22114", "22125"],
    "grundstück": ["21200", "22114", "22125"],
    "auflassung": ["21200", "22114", "22125"],
    "kaufvertrag": ["21200", "22114", "22125"],
    "grundstückskauf": ["21200", "22114", "22125", "23300"],
    "testament": ["21200"],
    "letztwillig": ["21200"],
    "erbe": ["21200"],
    "erblasser": ["21200"],
    "erbvertrag": ["21200", "22114", "22125"],
    "schenk": ["21200", "22114", "22125"],
    "schenkung": ["21200", "22114", "22125"],
    "schenkungsvertrag": ["21200", "22114", "22125"],
    "vollmacht": ["21200", "22125"],
    "betreuung": ["21200", "22125"],
    "vorsorgevollmacht": ["21200", "22125"],
    "grundschuld": ["23300"],
    "hypothek": ["23300"],
    "löschung": ["23200"],
    "beglaubigung": ["25100"],
    "bescheinigung": ["25200"],
    "beratung": ["24102"],
}


def suggest_missing_positions(
    extracted_positions: list[ExtractedPosition],
    document_type: str,
) -> list[dict[str, Any]]:
    """Vorschlägt fehlende KV-Positionen basierend auf dem Dokumententyp.

    Args:
        extracted_positions: Bereits vom LLM extrahierte Positionen.
        document_type: Vom LLM erkannter Dokumententyp.

    Returns:
        Liste von Vorschlags-Dictionaries, die der Nutzer übernehmen kann.
    """
    existing_kv_numbers = {p.kv_number for p in extracted_positions if p.kv_number}
    document_type_lower = document_type.lower()

    # Erwartete KV-Nummern für diesen Dokumententyp ermitteln
    expected_kv_numbers: set[str] = set()
    for keyword, expected_kvs in DOCUMENT_TYPE_EXPECTATIONS.items():
        if keyword in document_type_lower:
            expected_kv_numbers.update(expected_kvs)

    if not expected_kv_numbers:
        return []

    # Geschäftswert für Vorschläge aus bestehenden Positionen ableiten
    business_value = _derive_suggestion_value(extracted_positions)

    try:
        catalog = load_gnotkg_catalog()
    except Exception:
        catalog = {}

    suggestions: list[dict[str, Any]] = []
    for kv_number in sorted(expected_kv_numbers):
        if kv_number in existing_kv_numbers:
            continue

        entry = catalog.get(kv_number, {})
        title = entry.get("title", "Unbekannte Position")
        description = entry.get("description", "")

        suggestions.append(
            {
                "kv_number": kv_number,
                "description": title,
                "business_value_eur": business_value,
                "source_reference": "Vorschlag basierend auf Dokumententyp",
                "confidence": 0.6,
                "reasoning": (
                    f"Für '{document_type}' wird typischerweise die Position "
                    f"{kv_number} ({title}) in Betracht gezogen. "
                    f"Bitte Geschäftswert und Geltung prüfen."
                ),
                "catalog_description": description,
            }
        )

    return suggestions


def _derive_suggestion_value(extracted_positions: list[ExtractedPosition]) -> float | None:
    """Leitet einen sinnvollen Vorschlagswert aus den bestehenden Positionen ab."""
    values = [
        p.business_value_eur
        for p in extracted_positions
        if p.business_value_eur is not None and p.business_value_eur > 0
    ]
    if not values:
        return None
    return max(values)
