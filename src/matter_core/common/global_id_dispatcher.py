"""Global ID dispatcher for matter core objects."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GlobalIdDispatcher:
    """
    Function:
        Generate stable per-type object IDs for matter core instances.
    Args:
        prefix_by_object_type: Mapping from object type to uppercase ID prefix.
    Implementation Logic:
        Each object type owns an independent monotonic counter so IDs stay
        readable and collision-free across the core model.
    """

    prefix_by_object_type: dict[str, str] = field(
        default_factory=lambda: {
            "Atom": "ATOM",
            "Bond": "BOND",
            "Molecule": "MOL",
            "Matter": "MAT",
            "MatterIntmolInteraction": "MINT",
            "Mixture": "MIXT",
            "MixtureComponent": "MIXC",
        }
    )
    _counter_by_prefix: dict[str, int] = field(default_factory=dict)

    def next_id(self, object_type: str) -> str:
        """
        Function:
            Allocate the next stable ID for one matter core object type.
        Args:
            object_type: Canonical matter core object type name.
        Returns:
            str: Newly allocated stable ID.
        Implementation Logic:
            Object types are resolved to documented prefixes first, then the
            counter for that prefix is incremented and formatted as six digits.
        """

        if object_type not in self.prefix_by_object_type:
            raise KeyError(f"Unsupported object type for ID allocation: {object_type}")
        prefix = self.prefix_by_object_type[object_type]
        current_value = self._counter_by_prefix.get(prefix, 0) + 1
        self._counter_by_prefix[prefix] = current_value
        return f"{prefix}_{current_value:06d}"


GLOBAL_ID_DISPATCHER = GlobalIdDispatcher()
