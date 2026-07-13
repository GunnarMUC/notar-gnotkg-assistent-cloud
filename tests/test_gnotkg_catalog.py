"""Tests für den GNotKG-Katalog-Parser."""

import json
from pathlib import Path

import pytest

from core.gnotkg_catalog import (
    _categorize_kv,
    _parse_kv_entry,
    _split_kv_entries,
    build_gnotkg_catalog,
    format_catalog_for_prompt,
    load_anlage1_text,
    load_gnotkg_catalog,
    save_gnotkg_catalog,
)

MINIMAL_GNOTKG_XML = """<?xml version="1.0" encoding="UTF-8"?>
<dokumente>
    <norm>
        <metadaten>
            <enbez>Anlage 1 (zu § 3 Absatz 2)</enbez>
        </metadaten>
        <textdaten>
            <text>
                <Content>
                    <P>21100Beurkundung eines Vertrags</P>
                    <P>21200Beurkundung einer Erklärung..........10,00 – mindestens 25,00 €</P>
                    <P>23300Grundschuld..........0,5 ‰</P>
                    <P>25100Beglaubigung..........20,00 €</P>
                    <P>11100Gerichtliche Gebühr</P>
                </Content>
            </text>
        </textdaten>
    </norm>
    <norm>
        <metadaten>
            <enbez>§ 1</enbez>
        </metadaten>
    </norm>
</dokumente>
"""


def test_load_anlage1_text_finds_anlage(tmp_path: Path) -> None:
    xml_path = tmp_path / "gnotkg.xml"
    xml_path.write_text(MINIMAL_GNOTKG_XML, encoding="utf-8")

    text = load_anlage1_text(xml_path)

    assert "Anlage 1" in text
    assert "21200" in text
    assert "11100" in text


def test_load_anlage1_text_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.xml"

    with pytest.raises(FileNotFoundError):
        load_anlage1_text(missing)


def test_load_anlage1_text_no_anlage(tmp_path: Path) -> None:
    xml_path = tmp_path / "gnotkg.xml"
    xml_path.write_text(
        '<?xml version="1.0" ?><dokumente><norm><metadaten><enbez>§ 1</enbez></metadaten></norm></dokumente>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Anlage 1"):
        load_anlage1_text(xml_path)


def test_split_kv_entries_extracts_notary_kvs() -> None:
    text = "21200Beurkundung einer Erklärung..........10,00 € 22114Vollzug..........15,00 €"

    entries = _split_kv_entries(text)

    assert "21200" in entries
    assert "22114" in entries
    assert entries["21200"].startswith("21200Beurkundung")
    assert entries["22114"].startswith("22114Vollzug")


def test_split_kv_entries_ignores_reference_numbers() -> None:
    text = "Siehe auch 22114, 22125 und 21200Beurkundung einer Erklärung..........10,00 €"

    entries = _split_kv_entries(text)

    assert "22114" not in entries
    assert "22125" not in entries
    assert "21200" in entries


def test_parse_kv_entry_with_placeholder() -> None:
    raw = "21200Beurkundung einer Erklärung..........10,00 – mindestens 25,00 €"

    parsed = _parse_kv_entry(raw)

    assert parsed is not None
    assert parsed["kv_number"] == "21200"
    assert parsed["title"] == "Beurkundung einer Erklärung"
    assert parsed["multiplier"] == "10,00"
    assert parsed["min_fee"] == "25,00"
    assert parsed["category"] == "Beurkundung"


def test_parse_kv_entry_with_flat_fee() -> None:
    raw = "25100Beglaubigung..........20,00 €"

    parsed = _parse_kv_entry(raw)

    assert parsed is not None
    assert parsed["kv_number"] == "25100"
    assert parsed["title"] == "Beglaubigung"
    assert parsed["flat_fee"] == "20,00"
    assert parsed["multiplier"] is None


def test_parse_kv_entry_no_fee() -> None:
    raw = "21200Beurkundung einer Erklärung"

    parsed = _parse_kv_entry(raw)

    assert parsed is not None
    assert parsed["title"] == "Beurkundung einer Erklärung"
    assert parsed["multiplier"] is None
    assert parsed["flat_fee"] is None


def test_categorize_kv() -> None:
    assert _categorize_kv("21200") == "Beurkundung"
    assert _categorize_kv("22114") == "Vollzug/Betreuung/Treuhand"
    assert _categorize_kv("23300") == "Grundschuld/Löschung"
    assert _categorize_kv("24102") == "Beratung/Vertretung"
    assert _categorize_kv("25100") == "Beglaubigung/Bescheinigung"
    assert _categorize_kv("90000") == "Sonstiges"


def test_build_gnotkg_catalog_filters_notary_kvs(tmp_path: Path) -> None:
    xml_path = tmp_path / "gnotkg.xml"
    xml_path.write_text(MINIMAL_GNOTKG_XML, encoding="utf-8")

    catalog = build_gnotkg_catalog(xml_path)

    assert all(k.startswith("2") for k in catalog)
    assert "11100" not in catalog
    assert "21200" in catalog
    assert "25100" in catalog


def test_save_and_load_gnotkg_catalog_roundtrip(tmp_path: Path) -> None:
    xml_path = tmp_path / "gnotkg.xml"
    catalog_path = tmp_path / "catalog.json"
    xml_path.write_text(MINIMAL_GNOTKG_XML, encoding="utf-8")

    saved = save_gnotkg_catalog(catalog_path=catalog_path, xml_path=xml_path)

    assert saved.exists()
    assert saved == catalog_path

    catalog = load_gnotkg_catalog(catalog_path)
    assert "21200" in catalog
    assert catalog["21200"]["title"]


def test_load_gnotkg_catalog_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError, match="GNotKG-Katalog"):
        load_gnotkg_catalog(missing)


def test_format_catalog_for_prompt_with_catalog() -> None:
    catalog = {
        "21200": {
            "title": "Beurkundung",
            "description": "Erklärung",
            "multiplier": "10,00",
            "min_fee": "25,00",
            "flat_fee": None,
        },
        "25100": {
            "title": "Beglaubigung",
            "description": "Unterschrift",
            "multiplier": None,
            "min_fee": None,
            "flat_fee": "20,00",
        },
    }

    text = format_catalog_for_prompt(catalog)

    assert "GNotKG Anlage 1" in text
    assert "21200 – Beurkundung" in text
    assert "Multiplikator: 10,00" in text
    assert "25100 – Beglaubigung" in text
    assert "Pauschalgebühr: 20,00 €" in text


def test_format_catalog_for_prompt_with_file(tmp_path: Path, monkeypatch) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog = {
        "21200": {
            "title": "Beurkundung",
            "description": "Erklärung",
            "multiplier": None,
            "min_fee": None,
            "flat_fee": None,
        },
    }
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr("core.gnotkg_catalog.DEFAULT_CATALOG_PATH", catalog_path)

    text = format_catalog_for_prompt()

    assert "21200 – Beurkundung" in text
