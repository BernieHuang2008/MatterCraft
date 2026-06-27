"""
Build MatterCraft AtomPresetDatabase CSV from the approved source database.

Please use the following command to build the database:

    python -m matter_core.preset.build_atom_preset_database

"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

from .atom_preset_database_loader import (
    ATOM_PRESET_DATABASE_CANDIDATE_URL,
    DEFAULT_ATOM_PRESET_DATABASE_PATH,
)
from .atom_preset_metadata import (
    CHINESE_NAME_BY_SYMBOL,
    COMMON_CHARGES_BY_SYMBOL,
    COMMON_OXIDATION_STATES_BY_SYMBOL,
)


CSV_FIELDNAMES: list[str] = [
    "symbol",
    "englishName",
    "chineseName",
    "atomicNumber",
    "standardAtomicMass",
    "defaultMassNumber",
    "defaultElectronConfig",
    "commonMassNumbers",
    "commonCharges",
    "commonOxidationStates",
    "ionizationEnergyList",
    "electronAffinityList",
    "isMetal",
    "period",
    "family",
    "block",
]

GROUP_TO_FAMILY: dict[int, str] = {
    1: "IA",
    2: "IIA",
    3: "IIIB",
    4: "IVB",
    5: "VB",
    6: "VIB",
    7: "VIIB",
    8: "VIIIB",
    9: "VIIIB",
    10: "VIIIB",
    11: "IB",
    12: "IIB",
    13: "IIIA",
    14: "IVA",
    15: "VA",
    16: "VIA",
    17: "VIIA",
    18: "VIIIA",
}

ORBITAL_SLOT_COUNT_BY_SUBSHELL: dict[str, int] = {
    "s": 1,
    "p": 3,
    "d": 5,
    "f": 7,
}

TRANSITION_GROUPS: set[int] = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
MAX_SUPPORTED_ATOMIC_NUMBER = 118
NOBLE_GAS_EXPANSION_BY_TOKEN: dict[str, str] = {
    "[He]": "1s2",
    "[Ne]": "1s2 2s2 2p6",
    "[Ar]": "1s2 2s2 2p6 3s2 3p6",
    "[Kr]": "1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6",
    "[Xe]": "1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6",
    "[Rn]": "1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6",
}


def main() -> None:
    """
    Function:
        Convert the approved upstream periodic-table JSON into the MatterCraft atom preset CSV.
    Args:
        None.
    Returns:
        None.
    Implementation Logic:
        The command-line entry point reads either a remote JSON URL or a local
        JSON file, converts each element row into the documented CSV schema and
        writes the result to the project preset path.
    """

    parser = argparse.ArgumentParser(
        description="Build MatterCraft AtomPresetDatabase CSV from the approved JSON source.",
    )
    parser.add_argument(
        "--source",
        default=ATOM_PRESET_DATABASE_CANDIDATE_URL,
        help="Approved source JSON URL or a local JSON file path.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_ATOM_PRESET_DATABASE_PATH),
        help="Output CSV path.",
    )
    args = parser.parse_args()

    source_payload = load_source_payload(args.source)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written_row_count = 0

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for element_payload in source_payload["elements"]:
            if int(element_payload["number"]) > MAX_SUPPORTED_ATOMIC_NUMBER:
                continue
            writer.writerow(convert_element_to_csv_row(element_payload))
            written_row_count += 1

    print(f"Wrote {written_row_count} rows to {output_path}")


def load_source_payload(source: str) -> dict[str, Any]:
    """
    Function:
        Load the approved upstream JSON payload from a URL or local file.
    Args:
        source: Upstream source URL or local file path.
    Returns:
        dict[str, Any]: Parsed JSON payload.
    Implementation Logic:
        Supporting both remote and local sources makes the converter usable for
        both fresh downloads and repeatable offline rebuilds.
    """

    parsed_source = urlparse(source)
    if parsed_source.scheme in {"http", "https"}:
        with urlopen(source) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(source).read_text(encoding="utf-8"))


def convert_element_to_csv_row(element_payload: dict[str, Any]) -> dict[str, str]:
    """
    Function:
        Convert one upstream element payload into one MatterCraft CSV row.
    Args:
        element_payload: Raw upstream element JSON object.
    Returns:
        dict[str, str]: CSV row matching the documented schema.
    Implementation Logic:
        The converter maps available upstream fields directly, then fills gaps
        with deterministic local inference rules documented in code.
    """

    symbol = element_payload["symbol"]
    english_name = element_payload["name"]
    chinese_name = CHINESE_NAME_BY_SYMBOL.get(symbol, english_name)
    atomic_number = int(element_payload["number"])
    standard_atomic_mass = normalize_atomic_mass_value(element_payload.get("atomic_mass"))
    default_mass_number = infer_default_mass_number(standard_atomic_mass)
    electron_config = parse_electron_configuration(
        element_payload.get("electron_configuration")
        or element_payload.get("electron_configuration_semantic")
        or "",
    )
    group = normalize_group_value(element_payload.get("group"))
    category = str(element_payload.get("category", ""))
    oxidation_states = infer_common_oxidation_states(
        symbol=symbol,
        group=group,
        category=category,
    )
    common_charges = infer_common_charges(
        symbol=symbol,
        group=group,
        category=category,
        oxidation_states=oxidation_states,
    )

    row = {
        "symbol": symbol,
        "englishName": english_name,
        "chineseName": chinese_name,
        "atomicNumber": str(atomic_number),
        "standardAtomicMass": standard_atomic_mass,
        "defaultMassNumber": str(default_mass_number),
        "defaultElectronConfig": json.dumps(electron_config, ensure_ascii=False, separators=(",", ":")),
        "commonMassNumbers": json.dumps([default_mass_number], ensure_ascii=False, separators=(",", ":")),
        "commonCharges": json.dumps(common_charges, ensure_ascii=False, separators=(",", ":")),
        "commonOxidationStates": json.dumps(
            oxidation_states,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "ionizationEnergyList": json.dumps(
            convert_ionization_energies(element_payload.get("ionization_energies", [])),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "electronAffinityList": json.dumps(
            convert_electron_affinity(element_payload.get("electron_affinity")),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "isMetal": str(is_metal(category)).lower(),
        "period": str(int(element_payload["period"])),
        "family": infer_family(group=group, category=category),
        "block": infer_block(element_payload),
    }
    return row


def normalize_atomic_mass_value(raw_mass: Any) -> str:
    """
    Function:
        Normalize the upstream atomic-mass field into a stable decimal string.
    Args:
        raw_mass: Upstream atomic-mass value.
    Returns:
        str: Normalized atomic-mass string.
    Implementation Logic:
        The upstream data may store masses as numbers or strings with brackets,
        so the converter extracts the first numeric token and preserves it as a
        clean decimal string.
    """

    mass_text = str(raw_mass).strip()
    numeric_match = re.search(r"-?\d+(?:\.\d+)?", mass_text)
    if numeric_match is None:
        raise ValueError(f"Cannot parse atomic mass from value: {raw_mass}")
    numeric_value = Decimal(numeric_match.group(0))
    return format(numeric_value.normalize(), "f")


def infer_default_mass_number(standard_atomic_mass: str) -> int:
    """
    Function:
        Infer the default mass number from the normalized standard atomic mass.
    Args:
        standard_atomic_mass: Normalized atomic-mass string.
    Returns:
        int: Inferred default mass number.
    Implementation Logic:
        The approved upstream source does not provide isotope abundance tables,
        so the first implementation rounds the standard atomic mass to the
        nearest integer as a deterministic default-isotope approximation.
    """

    return int(Decimal(standard_atomic_mass).to_integral_value())


def parse_electron_configuration(configuration_text: str) -> dict[str, list[int]]:
    """
    Function:
        Parse upstream electron-configuration text into MatterCraft orbital payload format.
    Args:
        configuration_text: Upstream electron-configuration string.
    Returns:
        dict[str, list[int]]: MatterCraft orbital occupancy mapping.
    Implementation Logic:
        The parser strips noble-gas shorthand, tokenizes orbital counts and
        expands each token into Hund-rule-style occupancy lists.
    """

    cleaned_text = configuration_text
    for token, expanded_text in NOBLE_GAS_EXPANSION_BY_TOKEN.items():
        cleaned_text = cleaned_text.replace(token, expanded_text)
    token_list = re.findall(r"(\d[spdf]\d+)", cleaned_text)
    electron_config: dict[str, list[int]] = {}
    for token in token_list:
        orbital_label, electron_count = parse_orbital_token(token)
        electron_config[orbital_label] = expand_orbital_occupancy(
            subshell=orbital_label[-1],
            electron_count=electron_count,
        )
    return electron_config


def parse_orbital_token(token: str) -> tuple[str, int]:
    """
    Function:
        Parse one orbital token such as ``2p6``.
    Args:
        token: Orbital token.
    Returns:
        tuple[str, int]: Orbital label and total electron count.
    Implementation Logic:
        The token format is constrained and parsed with one regex so malformed
        upstream values fail loudly during conversion.
    """

    match = re.fullmatch(r"(\d[spdf])(\d+)", token)
    if match is None:
        raise ValueError(f"Unsupported orbital token: {token}")
    return match.group(1), int(match.group(2))


def expand_orbital_occupancy(subshell: str, electron_count: int) -> list[int]:
    """
    Function:
        Expand a total subshell electron count into a MatterCraft occupancy list.
    Args:
        subshell: Subshell letter such as ``s`` or ``p``.
        electron_count: Total electron count in that subshell.
    Returns:
        list[int]: Orbital occupancy list.
    Implementation Logic:
        The list fills each orbital singly first, then adds paired electrons,
        producing the format documented for ``bElectronConfig``.
    """

    slot_count = ORBITAL_SLOT_COUNT_BY_SUBSHELL[subshell]
    occupancy = [0] * slot_count
    remaining = electron_count
    for index in range(slot_count):
        if remaining <= 0:
            break
        occupancy[index] += 1
        remaining -= 1
    for index in range(slot_count):
        if remaining <= 0:
            break
        occupancy[index] += 1
        remaining -= 1
    return occupancy


def convert_ionization_energies(raw_values: Any) -> list[int]:
    """
    Function:
        Convert upstream ionization energies into MatterCraft ``J/mol`` integers.
    Args:
        raw_values: Upstream ionization-energy sequence in ``kJ/mol``.
    Returns:
        list[int]: Converted energy list in ``J/mol``.
    Implementation Logic:
        The approved upstream database stores ionization energies in ``kJ/mol``,
        so the converter multiplies by 1000 and rounds to the nearest integer.
    """

    energy_list: list[int] = []
    for value in raw_values or []:
        energy_list.append(int(Decimal(str(value)) * Decimal("1000")))
    return energy_list


def convert_electron_affinity(raw_value: Any) -> list[int]:
    """
    Function:
        Convert the upstream electron-affinity field into MatterCraft ``J/mol`` convention.
    Args:
        raw_value: Upstream electron-affinity value in ``kJ/mol``.
    Returns:
        list[int]: Converted list in ``J/mol`` using MatterCraft sign convention.
    Implementation Logic:
        The upstream source records energy release as positive values, while
        MatterCraft stores released energy as negative values, so the sign is flipped.
    """

    if raw_value in {None, ""}:
        return []
    return [int(Decimal(str(raw_value)) * Decimal("-1000"))]


def infer_family(group: int | None, category: str) -> str:
    """
    Function:
        Infer the family label required by the MatterCraft CSV schema.
    Args:
        group: Upstream group number if available.
        category: Upstream category text.
    Returns:
        str: Family label.
    Implementation Logic:
        The first implementation uses classic A/B group labels when a group is
        known and falls back to category-based special labels for f-block series.
    """

    lowered_category = category.lower()
    if "lanthanide" in lowered_category:
        return "Lanthanide"
    if "actinide" in lowered_category:
        return "Actinide"
    if group is None:
        return "Unknown"
    return GROUP_TO_FAMILY.get(group, "Unknown")


def infer_block(element_payload: dict[str, Any]) -> str:
    """
    Function:
        Infer the periodic-table block for one element.
    Args:
        element_payload: Raw upstream element JSON object.
    Returns:
        str: One of ``s``, ``p``, ``d`` or ``f``.
    Implementation Logic:
        The converter first trusts any explicit upstream block-like field and
        otherwise infers the block from electron configuration or category.
    """

    if "block" in element_payload and element_payload["block"]:
        return str(element_payload["block"]).lower()

    category = str(element_payload.get("category", "")).lower()
    if "lanthanide" in category or "actinide" in category:
        return "f"

    configuration_text = str(
        element_payload.get("electron_configuration_semantic")
        or element_payload.get("electron_configuration")
        or ""
    )
    token_list = re.findall(r"\d([spdf])\d+", configuration_text)
    if token_list:
        return token_list[-1]
    group = normalize_group_value(element_payload.get("group"))
    if group in {1, 2}:
        return "s"
    if group in TRANSITION_GROUPS:
        return "d"
    return "p"


def normalize_group_value(raw_group: Any) -> int | None:
    """
    Function:
        Normalize the upstream group field into an integer if possible.
    Args:
        raw_group: Upstream group value.
    Returns:
        int | None: Normalized group number.
    Implementation Logic:
        Some elements may omit a group number, so the helper returns ``None``
        instead of forcing every row into a fabricated group.
    """

    if raw_group in {None, ""}:
        return None
    try:
        return int(raw_group)
    except (TypeError, ValueError):
        return None


def is_metal(category: str) -> bool:
    """
    Function:
        Infer whether one element should be marked as a metal.
    Args:
        category: Upstream category text.
    Returns:
        bool: Metal classification result.
    Implementation Logic:
        The first implementation treats metalloid separately and marks every
        other category containing ``metal`` as metallic.
    """

    lowered_category = category.lower()
    if "nonmetal" in lowered_category:
        return False
    if "metalloid" in lowered_category:
        return False
    return "metal" in lowered_category


def infer_common_oxidation_states(
    symbol: str,
    group: int | None,
    category: str,
) -> list[int]:
    """
    Function:
        Infer the common oxidation states for one element.
    Args:
        symbol: Element symbol.
        group: Normalized group number.
        category: Upstream category text.
    Returns:
        list[int]: Sorted oxidation-state list.
    Implementation Logic:
        Hand-curated overrides are used first; otherwise the converter applies
        deterministic group/category heuristics for the initial database build.
    """

    if symbol in COMMON_OXIDATION_STATES_BY_SYMBOL:
        return COMMON_OXIDATION_STATES_BY_SYMBOL[symbol]

    lowered_category = category.lower()
    if "alkali metal" in lowered_category:
        return [0, 1]
    if "alkaline earth metal" in lowered_category:
        return [0, 2]
    if "lanthanide" in lowered_category:
        return [0, 3]
    if "actinide" in lowered_category:
        return [0, 3, 4]
    if group == 13:
        return [0, 3]
    if group == 14:
        return [-4, 0, 2, 4]
    if group == 15:
        return [-3, 0, 3, 5]
    if group == 16:
        return [-2, 0, 2, 4, 6]
    if group == 17:
        return [-1, 0, 1, 3, 5, 7]
    if group == 18:
        return [0]
    if group in TRANSITION_GROUPS:
        return [0, 2]
    return [0]


def infer_common_charges(
    symbol: str,
    group: int | None,
    category: str,
    oxidation_states: list[int],
) -> list[int]:
    """
    Function:
        Infer the common ion charges for one element.
    Args:
        symbol: Element symbol.
        group: Normalized group number.
        category: Upstream category text.
        oxidation_states: Inferred oxidation-state list.
    Returns:
        list[int]: Sorted common-charge list.
    Implementation Logic:
        Hand-curated overrides are preferred; otherwise the converter reuses a
        conservative subset of oxidation states as a first-pass ion list.
    """

    if symbol in COMMON_CHARGES_BY_SYMBOL:
        return COMMON_CHARGES_BY_SYMBOL[symbol]

    lowered_category = category.lower()
    if "alkali metal" in lowered_category:
        return [0, 1]
    if "alkaline earth metal" in lowered_category:
        return [0, 2]
    if group == 18:
        return [0]

    filtered_state_list = [
        state
        for state in oxidation_states
        if state == 0 or abs(state) <= 3
    ]
    if not filtered_state_list:
        return [0]
    return sorted(set(filtered_state_list))


if __name__ == "__main__":
    main()
