"""Numeric normalization helpers for matter core quantities."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any


FIELD_QUANTUM_BY_NAME: dict[str, str] = {
    "bAmount": "1e-12",
    "bBondEnergy": "1e-3",
    "bBondLength": "1e-13",
    "bPolarity": "1e-12",
    "bMetallicBondStrength": "1e-3",
    "bPhyMoleculeGap": "1e-12",
    "bInteractionStrength": "1e-3",
    "bInteractionDistance": "1e-12",
}


def normalize_decimal_string(value: int | float | str | Decimal, quantum: str) -> str:
    """
    Function:
        Quantize a numeric value and return a stable scientific-notation string.
    Args:
        value: Numeric input value.
        quantum: Decimal quantum string such as ``1e-12``.
    Returns:
        str: Stable decimal string ready for descriptor or hash usage.
    Implementation Logic:
        The helper follows the project rule that floating values entering stable
        structures should be quantized and serialized as deterministic strings.
    """

    quantized_value = Decimal(str(value)).quantize(
        Decimal(quantum),
        rounding=ROUND_HALF_UP,
    )
    digits = max(0, -Decimal(quantum).as_tuple().exponent)
    return format(quantized_value, f".{digits}e")


def normalize_field_value(field_name: str, value: Any) -> Any:
    """
    Function:
        Normalize a descriptor basic property according to field-specific rules.
    Args:
        field_name: Field name from the matter core object.
        value: Raw field value.
    Returns:
        Any: Normalized field value.
    Implementation Logic:
        Only fields explicitly documented as normalized numeric quantities are
        converted here; other fields pass through unchanged.
    """

    if value is None:
        return None
    if field_name in FIELD_QUANTUM_BY_NAME:
        return normalize_decimal_string(value=value, quantum=FIELD_QUANTUM_BY_NAME[field_name])
    return value
