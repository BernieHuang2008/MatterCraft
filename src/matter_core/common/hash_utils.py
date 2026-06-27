"""Canonical hashing utilities for matter core objects."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .units import normalize_field_value


def build_object_hash(object_type: str, descriptor: Any) -> str:
    """
    Function:
        Build the canonical SHA-256 property hash for one matter core object.
    Args:
        object_type: Canonical object type name.
        descriptor: Descriptor instance representing the stable object payload.
    Returns:
        str: Lowercase SHA-256 digest.
    Implementation Logic:
        The helper follows the documented hash flow: descriptor conversion,
        basic-property collection, canonical JSON serialization and SHA-256.
    """

    payload = {
        "hashSchemaVersion": 1,
        "objectType": object_type,
        "bProperties": canonicalize_for_hash(collect_basic_properties(descriptor)),
    }
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def collect_basic_properties(descriptor: Any) -> dict[str, Any]:
    """
    Function:
        Collect all documented basic properties from a descriptor instance.
    Args:
        descriptor: Descriptor instance.
    Returns:
        dict[str, Any]: Mapping containing only ``b``-prefixed properties.
    Implementation Logic:
        The project documentation states that only descriptor basic properties
        participate in the canonical hash payload.
    """

    raw_values = vars(descriptor)
    return {
        name: normalize_field_value(field_name=name, value=value)
        for name, value in raw_values.items()
        if name.startswith("b")
    }


def canonicalize_for_hash(value: Any) -> Any:
    """
    Function:
        Convert nested object graphs into canonical hash-safe payloads.
    Args:
        value: Arbitrary nested value.
    Returns:
        Any: Canonicalized hash payload fragment.
    Implementation Logic:
        Dict keys are sorted, ordered lists are preserved, sets are sorted by
        canonical JSON, and nested matter core objects contribute their hashes.
    """

    if hasattr(value, "hash") and callable(value.hash):
        return value.hash()
    if is_dataclass(value):
        return canonicalize_for_hash(asdict(value))
    if isinstance(value, dict):
        return {
            key: canonicalize_for_hash(value[key])
            for key in sorted(value.keys(), key=str)
        }
    if isinstance(value, list):
        return [canonicalize_for_hash(item) for item in value]
    if isinstance(value, tuple):
        return [canonicalize_for_hash(item) for item in value]
    if isinstance(value, set):
        canonical_items = [canonicalize_for_hash(item) for item in value]
        return sorted(
            canonical_items,
            key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
        )
    if isinstance(value, float):
        return format(value, ".12e")
    return value
