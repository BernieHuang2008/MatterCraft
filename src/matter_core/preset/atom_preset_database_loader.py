"""CSV loader and future source mapping utilities for AtomPresetDatabase."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ATOM_PRESET_DATABASE_CANDIDATE_URL = (
    "https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json"
)
DEFAULT_ATOM_PRESET_DATABASE_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "presets" / "atom_preset_database.csv"
)


@dataclass(slots=True)
class AtomPresetRecord:
    """
    Function:
        Represent one normalized CSV row from AtomPresetDatabase.
    Args:
        The fields mirror the current CSV documentation.
    Implementation Logic:
        A typed record keeps the loader output explicit and makes future Atom
        constructors independent from raw CSV string handling.
    """

    symbol: str
    englishName: str
    chineseName: str
    atomicNumber: int
    standardAtomicMass: str
    defaultMassNumber: int
    defaultElectronConfig: dict[str, list[int]]
    commonMassNumbers: list[int]
    commonCharges: list[int]
    commonOxidationStates: list[int]
    ionizationEnergyList: list[float]
    electronAffinityList: list[float]
    isMetal: bool
    period: int
    family: str
    block: str


class AtomPresetDatabaseLoader:
    """
    Function:
        Load the normalized AtomPresetDatabase CSV into typed records.
    Args:
        csv_path: Optional custom CSV path.
    Implementation Logic:
        The loader centralizes CSV parsing and JSON-field decoding so logic
        classes can focus on chemistry semantics instead of file handling.
    """

    def __init__(self, csv_path: Path | None = None) -> None:
        """
        Function:
            Initialize the loader with one CSV path.
        Args:
            csv_path: Optional CSV path override.
        Returns:
            None.
        Implementation Logic:
            The documented default path is used unless a caller injects a custom
            dataset for tests or future alternate preset packs.
        """

        self.csv_path = csv_path or DEFAULT_ATOM_PRESET_DATABASE_PATH

    def load(self) -> dict[str, AtomPresetRecord]:
        """
        Function:
            Load the full atom preset database from CSV.
        Args:
            None.
        Returns:
            dict[str, AtomPresetRecord]: Symbol-indexed preset records.
        Implementation Logic:
            Each CSV row is decoded into a typed record and stored by element
            symbol for the documented ``fromElementSymbol`` lookup flow.
        """

        if not self.csv_path.exists():
            raise FileNotFoundError(
                "Atom preset database CSV does not exist yet. "
                "Approve the candidate database URL first, then generate "
                f"the CSV at {self.csv_path}."
            )

        with self.csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return {
                row["symbol"]: self._row_to_record(row)
                for row in reader
            }

    def get_by_symbol(self, symbol: str) -> AtomPresetRecord:
        """
        Function:
            Return one atom preset record by element symbol.
        Args:
            symbol: Element symbol such as ``O`` or ``Na``.
        Returns:
            AtomPresetRecord: Matching preset record.
        Implementation Logic:
            Symbol lookup is the main path used by Atom logic constructors, so a
            convenience method keeps that call site clean.
        """

        database = self.load()
        if symbol not in database:
            raise KeyError(f"Unknown atom preset symbol: {symbol}")
        return database[symbol]

    @staticmethod
    def _row_to_record(row: dict[str, str]) -> AtomPresetRecord:
        """
        Function:
            Convert one CSV row into a typed atom preset record.
        Args:
            row: Raw CSV row mapping.
        Returns:
            AtomPresetRecord: Parsed record.
        Implementation Logic:
            The project documents several stringify-JSON columns, so the loader
            decodes them once here and returns already-typed values.
        """

        return AtomPresetRecord(
            symbol=row["symbol"],
            englishName=row["englishName"],
            chineseName=row["chineseName"],
            atomicNumber=int(row["atomicNumber"]),
            standardAtomicMass=row["standardAtomicMass"],
            defaultMassNumber=int(row["defaultMassNumber"]),
            defaultElectronConfig=json.loads(row["defaultElectronConfig"]),
            commonMassNumbers=[int(value) for value in json.loads(row["commonMassNumbers"])],
            commonCharges=[int(value) for value in json.loads(row["commonCharges"])],
            commonOxidationStates=[
                int(value) for value in json.loads(row["commonOxidationStates"])
            ],
            ionizationEnergyList=[
                float(value) for value in json.loads(row["ionizationEnergyList"])
            ],
            electronAffinityList=[
                float(value) for value in json.loads(row["electronAffinityList"])
            ],
            isMetal=_parse_bool_string(row["isMetal"]),
            period=int(row["period"]),
            family=row["family"],
            block=row["block"],
        )


def _parse_bool_string(value: str) -> bool:
    """
    Function:
        Convert the documented bool-string CSV format into a Python bool.
    Args:
        value: CSV bool string.
    Returns:
        bool: Parsed boolean value.
    Implementation Logic:
        The CSV format stores booleans as strings, so the loader normalizes them
        into real booleans at the file boundary.
    """

    return value.strip().lower() == "true"
