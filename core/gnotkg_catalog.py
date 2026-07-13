"""Parser für das GNotKG-Anlage-1-Kostenverzeichnis aus der gesetze-im-internet.de-XML.

Das Modul liest die Datei `Gesetze/BJNR258610013 3.xml`, extrahiert den Bereich
"Anlage 1 (zu § 3 Absatz 2)" und wandelt die Einzelpositionen (KV-Nummern) in
eine strukturierte JSON-Datei um.  Nur notarielle Gebührenpositionen
(KV-Nummern 2xxxxx) werden berücksichtigt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

from defusedxml import ElementTree

DEFAULT_GNOTKG_XML = Path("Gesetze/BJNR258610013 3.xml")
DEFAULT_CATALOG_PATH = Path("data/fee_tables/gnotkg_anlage1_catalog.json")


def _extract_all_text(element: ElementTree.Element) -> str:
    """Rekursive Textextraktion aus einem XML-Element."""
    text = element.text or ""
    for child in element:
        text += _extract_all_text(child)
        if child.tail:
            text += child.tail
    return text


def load_anlage1_text(xml_path: Path | str = DEFAULT_GNOTKG_XML) -> str:
    """Lädt die GNotKG-XML und liefert den reinen Text der Anlage 1 zurück."""
    xml_path = Path(xml_path)
    if not xml_path.exists():
        raise FileNotFoundError(f"GNotKG-XML nicht gefunden: {xml_path}")

    tree = ElementTree.parse(xml_path)
    root = tree.getroot()

    for norm in root.findall("norm"):
        enbez = norm.findtext("metadaten/enbez", "")
        if "Anlage 1" in enbez:
            return _extract_all_text(norm)

    raise ValueError("Anlage 1 in der GNotKG-XML nicht gefunden.")


def _split_kv_entries(text: str) -> dict[str, str]:
    """Splittet Anlage-1-Text anhand der KV-Nummern in einzelne Roh-Einträge."""
    # Eine Definitionsstelle ist eine 5-stellige Zahl, die direkt von einem
    # Großbuchstaben (Titelanfang) gefolgt wird. Referenzen wie "22114, 22125 und"
    # werden dadurch ignoriert.
    matches = list(re.finditer(r"(\d{5})(?=[A-Z])", text))
    entries: dict[str, str] = {}

    for i, match in enumerate(matches):
        kv_number = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw_entry = text[start:end]

        # Normalsiere Whitespace
        raw_entry = re.sub(r"\s+", " ", raw_entry).strip()

        # Nur den ersten, inhaltlichen Eintrag pro KV-Nummer behalten
        if kv_number not in entries:
            entries[kv_number] = raw_entry

    return entries


def _parse_kv_entry(raw_entry: str) -> dict[str, Any] | None:
    """Parsed einen Roh-Eintrag in Titel, Beschreibung und Gebührenangaben."""
    # Entferne führende KV-Nummer
    match = re.match(r"(\d{5})\s*(.*)", raw_entry)
    if not match:
        return None

    kv_number = match.group(1)
    remainder = match.group(2)

    # Trenne Titel und Beschreibung am Platzhalter ".........." oder am ersten Satzzeichen
    if ".........." in remainder:
        parts = re.split(r"\s*\.\.\.\.\.\.\.\.\.\s*", remainder, maxsplit=1)
        title = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""
    else:
        # Falls kein Platzhalter vorhanden ist, nehmen wir den ersten Satz als Titel
        first_sentence = re.split(r"(?<=[.:;])\s+(?=[A-ZÄÖÜ])", remainder, maxsplit=1)
        title = first_sentence[0].strip()
        description = first_sentence[1].strip() if len(first_sentence) > 1 else ""

    # Beschreibung an nächster KV-Definition oder Abschnittsüberschrift abschneiden
    description = re.split(r"(?<!\d)\d{5}(?=[A-Z])", description, maxsplit=1)[0].strip()
    description = re.split(
        r"(?:Abschnitt|Hauptabschnitt|Unterabschnitt|Vorbemerkung)\s+\d", description, maxsplit=1
    )[0].strip()

    # Suche Gebührenmultiplikator und Mindestgebühr
    value_fee_match = re.search(r"(\d+,\d+)\s*–\s*mindestens\s+([\d,]+)\s*€", raw_entry)
    multiplier: str | None = None
    min_fee: str | None = None
    if value_fee_match:
        multiplier = value_fee_match.group(1)
        min_fee = value_fee_match.group(2)

    # Suche Pauschalgebühren (z. B. "20,00 €")
    flat_fee_match = re.search(r"(\d+,\d+)\s*€(?!\s*–)", raw_entry)
    flat_fee: str | None = None
    if flat_fee_match and not value_fee_match:
        flat_fee = flat_fee_match.group(1)

    # Bereinige Titel von Preisangaben am Ende
    title = re.sub(r"\s+\d+,\d+.*€$", "", title).strip()

    # Kategorisierung anhand der KV-Nummer
    category = _categorize_kv(kv_number)

    return {
        "kv_number": kv_number,
        "title": title,
        "description": description,
        "category": category,
        "multiplier": multiplier,
        "min_fee": min_fee,
        "flat_fee": flat_fee,
    }


def _categorize_kv(kv_number: str) -> str:
    """Ordnet eine KV-Nummer einer notariellen Kategorie zu."""
    prefix = kv_number[:2]
    category_map = {
        "21": "Beurkundung",
        "22": "Vollzug/Betreuung/Treuhand",
        "23": "Grundschuld/Löschung",
        "24": "Beratung/Vertretung",
        "25": "Beglaubigung/Bescheinigung",
    }
    return category_map.get(prefix, "Sonstiges")


def build_gnotkg_catalog(
    xml_path: Path | str = DEFAULT_GNOTKG_XML,
) -> dict[str, dict[str, Any]]:
    """Baut aus der GNotKG-XML einen strukturierten KV-Katalog auf."""
    text = load_anlage1_text(xml_path)
    raw_entries = _split_kv_entries(text)

    catalog: dict[str, dict[str, Any]] = {}
    for kv_number, raw_entry in raw_entries.items():
        # Nur notarielle KV-Nummern (2xxxxx) für diesen Assistenten
        if not kv_number.startswith("2"):
            continue

        parsed = _parse_kv_entry(raw_entry)
        if parsed and parsed["title"]:
            catalog[kv_number] = parsed

    return catalog


def load_gnotkg_catalog(
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
) -> dict[str, dict[str, Any]]:
    """Lädt den vorberechneten KV-Katalog aus einer JSON-Datei."""
    catalog_path = Path(catalog_path)
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"GNotKG-Katalog nicht gefunden: {catalog_path}. "
            "Bitte zuerst mit save_gnotkg_catalog() generieren."
        )

    with catalog_path.open(encoding="utf-8") as f:
        return cast(dict[str, dict[str, Any]], json.load(f))


def save_gnotkg_catalog(
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
    xml_path: Path | str = DEFAULT_GNOTKG_XML,
) -> Path:
    """Generiert und speichert den KV-Katalog als JSON."""
    catalog = build_gnotkg_catalog(xml_path)
    catalog_path = Path(catalog_path)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    with catalog_path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    return catalog_path


def format_catalog_for_prompt(catalog: dict[str, dict[str, Any]] | None = None) -> str:
    """Formatiert den Katalog kompakt für die Verwendung im LLM-Prompt."""
    if catalog is None:
        catalog = load_gnotkg_catalog()

    lines = ["GNotKG Anlage 1 – Kostenverzeichnis (notarielle Gebühren):", ""]
    for kv_number in sorted(catalog.keys()):
        entry = catalog[kv_number]
        title = entry.get("title", "")
        description = entry.get("description", "")
        fee_info = ""
        if entry.get("multiplier"):
            fee_info = f" | Multiplikator: {entry['multiplier']}"
        if entry.get("min_fee"):
            fee_info += f", Mindestgebühr: {entry['min_fee']} €"
        if entry.get("flat_fee"):
            fee_info = f" | Pauschalgebühr: {entry['flat_fee']} €"

        lines.append(f"{kv_number} – {title}{fee_info}")
        if description:
            # Beschreibung auf eine Zeile komprimieren
            short_desc = re.sub(r"\s+", " ", description).strip()
            if short_desc:
                lines.append(f"  {short_desc}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    out = save_gnotkg_catalog()
    print(f"Katalog gespeichert: {out}")
    catalog = load_gnotkg_catalog()
    print(f"Anzahl notarieller KV-Positionen: {len(catalog)}")
    for kv in ["21200", "22114", "22125", "23300"]:
        if kv in catalog:
            print(f"\n{kv}: {catalog[kv]}")
