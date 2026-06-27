"""Atom LDC classes for MatterCraft."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import ClassVar

from matter_core.common import GLOBAL_ID_DISPATCHER, MatterCalculusBase, MatterDescriptorBase, MatterLogicBase
from matter_core.preset import AtomPresetDatabaseLoader


ORBITAL_SLOT_COUNT_BY_SUBSHELL: dict[str, int] = {
    "s": 1,
    "p": 3,
    "d": 5,
    "f": 7,
}

SUBSHELL_ORDER: dict[str, int] = {
    "s": 0,
    "p": 1,
    "d": 2,
    "f": 3,
}


@dataclass(slots=True)
class AtomDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one atom or ion.
    Args:
        _id: Stable instance ID.
        bAtomicNumber: Atomic number.
        bMassNumber: Mass number.
        bCharge: Formal charge in elementary-charge units.
        bElectronConfig: Orbital occupancy map.
    Implementation Logic:
        The descriptor keeps only stable basic properties so it can be hashed,
        serialized and converted into other LDC versions.
    """

    _object_type: ClassVar[str] = "Atom"
    _debug_module: ClassVar[str] = "descriptor.atom"

    _id: str
    bAtomicNumber: int
    bMassNumber: int
    bCharge: int
    bElectronConfig: dict[str, list[int]]

    def __post_init__(self) -> None:
        """
        Function:
            Validate the descriptor and publish a creation debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Simple invariant checks catch malformed descriptors early and the
            debug event helps track object construction.
        """

        if self.bAtomicNumber <= 0:
            raise ValueError("bAtomicNumber must be positive.")
        if self.bMassNumber < self.bAtomicNumber:
            raise ValueError("bMassNumber must not be smaller than bAtomicNumber.")
        self._log_debug(
            message="AtomDescriptor created.",
            context={"_id": self._id, "atomicNumber": self.bAtomicNumber, "charge": self.bCharge},
        )


@dataclass(slots=True)
class AtomCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one atom or ion.
    Args:
        _id: Stable instance ID.
        bAtomicNumber: Atomic number.
        bMassNumber: Mass number.
        bCharge: Formal charge.
        bElectronConfig: Orbital occupancy map.
    Implementation Logic:
        The first calculus version keeps the same stable payload as the
        descriptor while exposing cached derived counts for future optimization.
    """

    _object_type: ClassVar[str] = "Atom"
    _debug_module: ClassVar[str] = "calculus.atom"

    _id: str
    bAtomicNumber: int
    bMassNumber: int
    bCharge: int
    bElectronConfig: dict[str, list[int]]

    @property
    def aElectronCount(self) -> int:
        """
        Function:
            Return the derived electron count of the current atom.
        Args:
            None.
        Returns:
            int: Derived electron count.
        Implementation Logic:
            The calculation follows the documented relation between atomic
            number and formal charge.
        """

        return self.bAtomicNumber - self.bCharge

    @property
    def aValenceElectronCount(self) -> int:
        """
        Function:
            Return the derived valence electron count.
        Args:
            None.
        Returns:
            int: Valence electron count.
        Implementation Logic:
            The calculation sums the electrons in the outermost occupied
            principal shell.
        """

        return count_valence_electrons(self.bElectronConfig)

    def toDescriptor(self) -> AtomDescriptor:
        """
        Function:
            Convert the calculus version back into a descriptor.
        Args:
            None.
        Returns:
            AtomDescriptor: Stable atom descriptor.
        Implementation Logic:
            The conversion copies only stable basic properties so hash
            consistency remains identical across LDC versions.
        """

        return AtomDescriptor(
            _id=self._id,
            bAtomicNumber=self.bAtomicNumber,
            bMassNumber=self.bMassNumber,
            bCharge=self.bCharge,
            bElectronConfig=deepcopy(self.bElectronConfig),
        )

    @classmethod
    def fromDescriptor(cls, descriptor: AtomDescriptor) -> "AtomCalculus":
        """
        Function:
            Build a calculus object from an atom descriptor.
        Args:
            descriptor: Source atom descriptor.
        Returns:
            AtomCalculus: New calculus object.
        Implementation Logic:
            The first calculus version mirrors descriptor data directly so later
            optimizations can evolve without breaking the interface.
        """

        instance = cls(
            _id=descriptor._id,
            bAtomicNumber=descriptor.bAtomicNumber,
            bMassNumber=descriptor.bMassNumber,
            bCharge=descriptor.bCharge,
            bElectronConfig=deepcopy(descriptor.bElectronConfig),
        )
        instance._log_debug(message="AtomCalculus created from descriptor.", context={"_id": instance._id})
        return instance


@dataclass(slots=True)
class AtomLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one atom or ion.
    Args:
        _id: Stable instance ID.
        bAtomicNumber: Atomic number.
        bMassNumber: Mass number.
        bCharge: Formal charge.
        bElectronConfig: Orbital occupancy map.
    Implementation Logic:
        The logic version is the primary entry point for object creation,
        automatic-property access and LDC conversion.
    """

    _object_type: ClassVar[str] = "Atom"
    _debug_module: ClassVar[str] = "logic.atom"

    _id: str
    bAtomicNumber: int
    bMassNumber: int
    bCharge: int
    bElectronConfig: dict[str, list[int]]

    def __post_init__(self) -> None:
        """
        Function:
            Validate the logic object and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The logic layer performs lightweight validation so malformed atoms
            are rejected before they spread into larger structures.
        """

        if self.bAtomicNumber <= 0:
            raise ValueError("bAtomicNumber must be positive.")
        if self.bMassNumber < self.bAtomicNumber:
            raise ValueError("bMassNumber must not be smaller than bAtomicNumber.")
        self._log_debug(
            message="AtomLogic created.",
            context={"_id": self._id, "atomicNumber": self.bAtomicNumber, "charge": self.bCharge},
        )

    @property
    def aProtonCount(self) -> int:
        """
        Function:
            Return the proton count derived from the atomic number.
        Args:
            None.
        Returns:
            int: Proton count.
        Implementation Logic:
            The project defines proton count to equal atomic number exactly.
        """

        return self.bAtomicNumber

    @property
    def aNeutronCount(self) -> int:
        """
        Function:
            Return the neutron count derived from atomic and mass numbers.
        Args:
            None.
        Returns:
            int: Neutron count.
        Implementation Logic:
            The calculation follows the documented mass-number relation.
        """

        return self.bMassNumber - self.bAtomicNumber

    @property
    def aElectronCount(self) -> int:
        """
        Function:
            Return the electron count derived from charge state.
        Args:
            None.
        Returns:
            int: Electron count.
        Implementation Logic:
            Neutral atoms and ions differ only by the formal charge delta.
        """

        return self.bAtomicNumber - self.bCharge

    @property
    def aValenceElectronCount(self) -> int:
        """
        Function:
            Return the derived valence electron count.
        Args:
            None.
        Returns:
            int: Valence electron count.
        Implementation Logic:
            The outermost occupied shell is treated as the valence shell in this
            first implementation.
        """

        return count_valence_electrons(self.bElectronConfig)

    def toDescriptor(self) -> AtomDescriptor:
        """
        Function:
            Convert the logic object into a stable descriptor.
        Args:
            None.
        Returns:
            AtomDescriptor: Stable atom descriptor.
        Implementation Logic:
            Descriptor conversion copies only stable basic properties so runtime
            state does not leak into hashes or storage.
        """

        descriptor = AtomDescriptor(
            _id=self._id,
            bAtomicNumber=self.bAtomicNumber,
            bMassNumber=self.bMassNumber,
            bCharge=self.bCharge,
            bElectronConfig=deepcopy(self.bElectronConfig),
        )
        self._log_debug(message="AtomLogic converted to descriptor.", context={"_id": self._id})
        return descriptor

    def toCalculus(self) -> AtomCalculus:
        """
        Function:
            Convert the logic object into a calculus representation.
        Args:
            None.
        Returns:
            AtomCalculus: Computation-oriented atom.
        Implementation Logic:
            The logic layer is the LDC conversion center, matching the project
            documentation for version translation.
        """

        calculus = AtomCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(message="AtomLogic converted to calculus.", context={"_id": self._id})
        return calculus

    @classmethod
    def fromDescriptor(cls, descriptor: AtomDescriptor) -> "AtomLogic":
        """
        Function:
            Build an atom logic object from a descriptor.
        Args:
            descriptor: Source descriptor.
        Returns:
            AtomLogic: New logic object.
        Implementation Logic:
            Descriptor-to-logic conversion restores the primary business-layer
            object without altering stable properties.
        """

        instance = cls(
            _id=descriptor._id,
            bAtomicNumber=descriptor.bAtomicNumber,
            bMassNumber=descriptor.bMassNumber,
            bCharge=descriptor.bCharge,
            bElectronConfig=deepcopy(descriptor.bElectronConfig),
        )
        instance._log_debug(message="AtomLogic created from descriptor.", context={"_id": instance._id})
        return instance

    @classmethod
    def fromCalculus(cls, calculus: AtomCalculus) -> "AtomLogic":
        """
        Function:
            Build an atom logic object from a calculus version.
        Args:
            calculus: Source calculus object.
        Returns:
            AtomLogic: New logic object.
        Implementation Logic:
            Calculus conversion routes through the descriptor representation to
            keep version behavior aligned.
        """

        return cls.fromDescriptor(calculus.toDescriptor())

    @classmethod
    def fromElementSymbol(
        cls,
        symbol: str,
        massNumber: int | None = None,
        charge: int = 0,
        electronConfig: dict[str, list[int]] | None = None,
        loader: AtomPresetDatabaseLoader | None = None,
    ) -> "AtomLogic":
        """
        Function:
            Build an atom from the atom preset database using an element symbol.
        Args:
            symbol: Element symbol.
            massNumber: Optional explicit mass number override.
            charge: Formal charge override.
            electronConfig: Optional explicit orbital occupancy override.
            loader: Optional preset database loader override.
        Returns:
            AtomLogic: New atom logic object.
        Implementation Logic:
            The constructor uses the preset database for stable default values,
            then applies explicit overrides according to the documentation.
        """

        active_loader = loader or AtomPresetDatabaseLoader()
        record = active_loader.get_by_symbol(symbol)
        resolved_mass_number = massNumber if massNumber is not None else record.defaultMassNumber
        resolved_config = (
            deepcopy(electronConfig)
            if electronConfig is not None
            else adjust_electron_config_for_charge(record.defaultElectronConfig, charge)
        )
        instance = cls(
            _id=GLOBAL_ID_DISPATCHER.next_id("Atom"),
            bAtomicNumber=record.atomicNumber,
            bMassNumber=resolved_mass_number,
            bCharge=charge,
            bElectronConfig=resolved_config,
        )
        instance._log_debug(
            message="AtomLogic created from element symbol.",
            context={"symbol": symbol, "_id": instance._id},
        )
        return instance

    @classmethod
    def fromPreset(
        cls,
        presetId: str,
        charge: int | None = None,
        electronConfig: dict[str, list[int]] | None = None,
        loader: AtomPresetDatabaseLoader | None = None,
    ) -> "AtomLogic":
        """
        Function:
            Build an atom from a preset identifier.
        Args:
            presetId: Preset identifier such as ``O16``.
            charge: Optional charge override.
            electronConfig: Optional explicit orbital occupancy override.
            loader: Optional preset database loader override.
        Returns:
            AtomLogic: New atom logic object.
        Implementation Logic:
            The first preset implementation accepts element-symbol-plus-mass
            identifiers and resolves them back through ``fromElementSymbol``.
        """

        match = re.fullmatch(r"([A-Z][a-z]?)(\d+)?", presetId)
        if match is None:
            raise ValueError(f"Unsupported presetId format: {presetId}")
        symbol = match.group(1)
        mass_number = int(match.group(2)) if match.group(2) else None
        resolved_charge = 0 if charge is None else charge
        return cls.fromElementSymbol(
            symbol=symbol,
            massNumber=mass_number,
            charge=resolved_charge,
            electronConfig=electronConfig,
            loader=loader,
        )


def count_valence_electrons(electron_config: dict[str, list[int]]) -> int:
    """
    Function:
        Count valence electrons from an orbital occupancy map.
    Args:
        electron_config: Orbital occupancy map.
    Returns:
        int: Valence electron count.
    Implementation Logic:
        The first implementation treats the highest occupied principal shell as
        the valence shell and sums all electrons in that shell.
    """

    if not electron_config:
        return 0
    highest_shell = max(_parse_orbital_label(label)[0] for label in electron_config.keys())
    return sum(sum(occupancy) for label, occupancy in electron_config.items() if _parse_orbital_label(label)[0] == highest_shell)


def adjust_electron_config_for_charge(
    base_config: dict[str, list[int]],
    charge: int,
) -> dict[str, list[int]]:
    """
    Function:
        Adjust a neutral default electron configuration for a target charge state.
    Args:
        base_config: Neutral baseline electron configuration.
        charge: Target formal charge.
    Returns:
        dict[str, list[int]]: Adjusted orbital occupancy map.
    Implementation Logic:
        Positive charge removes electrons from outer higher-energy orbitals,
        while negative charge adds electrons using a simple Aufbau-style order.
    """

    flat = _flatten_electron_config(base_config)
    adjusted = dict(flat)

    if charge > 0:
        for _ in range(charge):
            orbital_to_remove = _select_orbital_for_removal(adjusted)
            if orbital_to_remove is None:
                raise ValueError("Cannot remove more electrons from the provided configuration.")
            adjusted[orbital_to_remove] -= 1
    elif charge < 0:
        for _ in range(abs(charge)):
            orbital_to_add = _select_orbital_for_addition(adjusted)
            if orbital_to_add is None:
                raise ValueError("Cannot add more electrons to the provided configuration.")
            adjusted[orbital_to_add] += 1

    return _inflate_electron_config(adjusted)


def _flatten_electron_config(electron_config: dict[str, list[int]]) -> dict[str, int]:
    """
    Function:
        Collapse orbital occupancy lists into total electron counts per orbital label.
    Args:
        electron_config: Orbital occupancy map.
    Returns:
        dict[str, int]: Total electrons per orbital label.
    Implementation Logic:
        Charge adjustment is easier on total counts, then the structure is
        expanded back into Hund-style occupancy lists.
    """

    return {label: sum(occupancy) for label, occupancy in electron_config.items()}


def _inflate_electron_config(electron_counts: dict[str, int]) -> dict[str, list[int]]:
    """
    Function:
        Expand total orbital electron counts back into occupancy lists.
    Args:
        electron_counts: Total electron counts per orbital label.
    Returns:
        dict[str, list[int]]: Expanded occupancy map.
    Implementation Logic:
        Expansion follows the documented orbital-list structure and a basic
        Hund-rule filling sequence.
    """

    expanded: dict[str, list[int]] = {}
    for label in sorted(electron_counts.keys(), key=_sort_key_for_addition):
        count = electron_counts[label]
        if count <= 0:
            continue
        subshell = label[-1]
        slot_count = ORBITAL_SLOT_COUNT_BY_SUBSHELL[subshell]
        occupancy = [0] * slot_count
        remaining = count
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
        expanded[label] = occupancy
    return expanded


def _select_orbital_for_removal(electron_counts: dict[str, int]) -> str | None:
    """
    Function:
        Select the next orbital from which one electron should be removed.
    Args:
        electron_counts: Total electron counts per orbital label.
    Returns:
        str | None: Selected orbital label, or ``None`` if nothing can be removed.
    Implementation Logic:
        Electron removal prioritizes the outermost orbitals by principal shell,
        then higher subshell order within the same shell.
    """

    candidates = [label for label, count in electron_counts.items() if count > 0]
    if not candidates:
        return None
    return max(candidates, key=_sort_key_for_removal)


def _select_orbital_for_addition(electron_counts: dict[str, int]) -> str | None:
    """
    Function:
        Select the next orbital that should receive one additional electron.
    Args:
        electron_counts: Total electron counts per orbital label.
    Returns:
        str | None: Selected orbital label, or ``None`` if nothing can be filled.
    Implementation Logic:
        Electron addition follows a simple Aufbau-style ordering based on
        ``n + l`` and then principal shell.
    """

    candidates = [
        label
        for label, count in electron_counts.items()
        if count < ORBITAL_SLOT_COUNT_BY_SUBSHELL[label[-1]] * 2
    ]
    if not candidates:
        return None
    return min(candidates, key=_sort_key_for_addition)


def _parse_orbital_label(label: str) -> tuple[int, int]:
    """
    Function:
        Parse an orbital label such as ``3p`` into sortable numeric parts.
    Args:
        label: Orbital label.
    Returns:
        tuple[int, int]: Principal shell and subshell order.
    Implementation Logic:
        The helper gives the module one canonical interpretation of orbital
        labels for both filling and electron-removal heuristics.
    """

    principal_shell = int(label[:-1])
    subshell_order = SUBSHELL_ORDER[label[-1]]
    return principal_shell, subshell_order


def _sort_key_for_addition(label: str) -> tuple[int, int, int]:
    """
    Function:
        Build a sort key for electron addition order.
    Args:
        label: Orbital label.
    Returns:
        tuple[int, int, int]: Sorting key.
    Implementation Logic:
        Aufbau ordering is approximated with ``n + l`` first and ``n`` second.
    """

    principal_shell, subshell_order = _parse_orbital_label(label)
    return principal_shell + subshell_order, principal_shell, subshell_order


def _sort_key_for_removal(label: str) -> tuple[int, int]:
    """
    Function:
        Build a sort key for electron removal order.
    Args:
        label: Orbital label.
    Returns:
        tuple[int, int]: Sorting key.
    Implementation Logic:
        Electron removal is approximated by removing from higher shells first
        and higher subshells within the same shell.
    """

    principal_shell, subshell_order = _parse_orbital_label(label)
    return principal_shell, subshell_order
