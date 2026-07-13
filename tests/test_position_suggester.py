"""Tests für den Vorschlags-Generator für fehlende GNotKG-Positionen."""

from core.models import ExtractedPosition
from core.position_suggester import _derive_suggestion_value, suggest_missing_positions


def _make_position(
    kv_number: str, business_value: float | None, description: str = ""
) -> ExtractedPosition:
    return ExtractedPosition(
        kv_number=kv_number,
        description=description,
        business_value_eur=business_value,
        source_reference="Test",
        confidence=1.0,
        reasoning="",
    )


def test_suggest_missing_positions_for_kaufvertrag() -> None:
    positions = [_make_position("21200", 150_000.0, "Beurkundung")]

    suggestions = suggest_missing_positions(positions, "Grundstückskaufvertrag")

    kv_numbers = {s["kv_number"] for s in suggestions}
    assert "22114" in kv_numbers
    assert "22125" in kv_numbers
    assert "23300" in kv_numbers
    assert "21200" not in kv_numbers


def test_suggest_missing_positions_inherits_business_value() -> None:
    positions = [_make_position("21200", 150_000.0)]

    suggestions = suggest_missing_positions(positions, "Kaufvertrag")

    for suggestion in suggestions:
        assert suggestion["business_value_eur"] == 150_000.0


def test_suggest_missing_positions_no_match() -> None:
    positions = [_make_position("21200", 100_000.0)]

    suggestions = suggest_missing_positions(positions, "Unbekannter Dokumententyp")

    assert suggestions == []


def test_suggest_missing_positions_already_complete() -> None:
    positions = [
        _make_position("21200", 100_000.0),
        _make_position("22114", 100_000.0),
        _make_position("22125", 100_000.0),
    ]

    suggestions = suggest_missing_positions(positions, "Kaufvertrag")

    assert suggestions == []


def test_suggest_missing_positions_catalog_description() -> None:
    positions: list[ExtractedPosition] = []

    suggestions = suggest_missing_positions(positions, "Testament")

    assert len(suggestions) == 1
    assert suggestions[0]["kv_number"] == "21200"
    assert "Dokumententyp" in suggestions[0]["source_reference"]
    assert suggestions[0]["confidence"] == 0.6


def test_derive_suggestion_value_returns_max() -> None:
    positions = [
        _make_position("21200", 50_000.0),
        _make_position("22114", 150_000.0),
        _make_position("22125", 80_000.0),
    ]

    value = _derive_suggestion_value(positions)

    assert value == 150_000.0


def test_derive_suggestion_value_no_values() -> None:
    positions = [
        _make_position("21200", None),
        _make_position("22114", 0.0),
    ]

    value = _derive_suggestion_value(positions)

    assert value is None


def test_suggest_missing_positions_with_zero_value() -> None:
    positions = [_make_position("21200", 0.0)]

    suggestions = suggest_missing_positions(positions, "Kaufvertrag")

    for suggestion in suggestions:
        assert suggestion["business_value_eur"] is None


def test_suggest_missing_positions_multiple_keywords() -> None:
    positions: list[ExtractedPosition] = []

    suggestions = suggest_missing_positions(positions, "Schenkungsvertrag")

    kv_numbers = {s["kv_number"] for s in suggestions}
    assert "21200" in kv_numbers
    assert "22114" in kv_numbers
    assert "22125" in kv_numbers


def test_suggest_missing_positions_ignores_empty_kv_number() -> None:
    positions: list[ExtractedPosition] = [
        ExtractedPosition(
            kv_number="",
            description="Allgemein",
            business_value_eur=100_000.0,
            source_reference="Test",
            confidence=1.0,
            reasoning="",
        )
    ]

    suggestions = suggest_missing_positions(positions, "Kaufvertrag")

    assert "21200" in {s["kv_number"] for s in suggestions}
