"""Matter LDC classes for MatterCraft."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, ClassVar

from matter_core.common import MatterCalculusBase, MatterDescriptorBase, MatterLogicBase
from matter_core.common.units import normalize_field_value

from .matter_intmol_interaction import (
    MatterIntmolInteractionCalculus,
    MatterIntmolInteractionDescriptor,
    MatterIntmolInteractionLogic,
)
from .molecule import MoleculeCalculus, MoleculeDescriptor, MoleculeLogic


@dataclass(slots=True)
class MatterDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one matter unit.
    Args:
        _id: Stable instance ID.
        bChemMoleculeList: Molecule mapping keyed by molecule ID.
        bPhyMoleculeGap: Molecule-gap quantity in normalized string form.
        bPhyMoleculeArrangement: Serializable arrangement descriptor.
        bMatterIntmolInteractionList: Matter-level weak-interaction collection.
    Implementation Logic:
        The descriptor separates chemistry and physical-organization properties
        at the Matter layer as documented.
    """

    _object_type: ClassVar[str] = "Matter"
    _debug_module: ClassVar[str] = "descriptor.matter"

    _id: str
    bChemMoleculeList: dict[str, MoleculeDescriptor]
    bPhyMoleculeGap: str | None = None
    bPhyMoleculeArrangement: dict[str, Any] | None = None
    bMatterIntmolInteractionList: list[MatterIntmolInteractionDescriptor] | None = None

    def __post_init__(self) -> None:
        """
        Function:
            Normalize numeric fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The descriptor normalizes the documented physical gap field at the
            boundary where stable matter payloads are created.
        """

        self.bPhyMoleculeGap = normalize_field_value("bPhyMoleculeGap", self.bPhyMoleculeGap)
        self._log_debug(
            message="MatterDescriptor created.",
            context={
                "_id": self._id,
                "moleculeCount": len(self.bChemMoleculeList),
                "interactionCount": len(self.bMatterIntmolInteractionList or []),
            },
        )


@dataclass(slots=True)
class MatterCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one matter unit.
    Args:
        The fields mirror the first descriptor-based matter calculus layout.
    Implementation Logic:
        The first calculus version preserves descriptor semantics while opening a
        future path for optimized arrangement and interaction indexing.
    """

    _object_type: ClassVar[str] = "Matter"
    _debug_module: ClassVar[str] = "calculus.matter"

    _id: str
    bChemMoleculeList: dict[str, MoleculeCalculus]
    bPhyMoleculeGap: str | None = None
    bPhyMoleculeArrangement: dict[str, Any] | None = None
    bMatterIntmolInteractionList: list[MatterIntmolInteractionCalculus] | None = None

    def toDescriptor(self) -> MatterDescriptor:
        """
        Function:
            Convert the calculus matter object into a stable descriptor.
        Args:
            None.
        Returns:
            MatterDescriptor: Stable matter descriptor.
        Implementation Logic:
            Nested molecule and interaction members are converted back into their
            descriptor forms before the outer descriptor is assembled.
        """

        return MatterDescriptor(
            _id=self._id,
            bChemMoleculeList={
                molecule_id: molecule.toDescriptor()
                for molecule_id, molecule in self.bChemMoleculeList.items()
            },
            bPhyMoleculeGap=self.bPhyMoleculeGap,
            bPhyMoleculeArrangement=deepcopy(self.bPhyMoleculeArrangement),
            bMatterIntmolInteractionList=[
                interaction.toDescriptor()
                for interaction in (self.bMatterIntmolInteractionList or [])
            ],
        )

    @classmethod
    def fromDescriptor(cls, descriptor: MatterDescriptor) -> "MatterCalculus":
        """
        Function:
            Build a matter calculus object from a descriptor.
        Args:
            descriptor: Source matter descriptor.
        Returns:
            MatterCalculus: New calculus object.
        Implementation Logic:
            Nested structure is translated member-by-member into calculus
            objects, preserving the documented Matter layer split.
        """

        instance = cls(
            _id=descriptor._id,
            bChemMoleculeList={
                molecule_id: MoleculeCalculus.fromDescriptor(molecule)
                for molecule_id, molecule in descriptor.bChemMoleculeList.items()
            },
            bPhyMoleculeGap=descriptor.bPhyMoleculeGap,
            bPhyMoleculeArrangement=deepcopy(descriptor.bPhyMoleculeArrangement),
            bMatterIntmolInteractionList=[
                MatterIntmolInteractionCalculus.fromDescriptor(interaction)
                for interaction in (descriptor.bMatterIntmolInteractionList or [])
            ],
        )
        instance._log_debug(message="MatterCalculus created from descriptor.", context={"_id": instance._id})
        return instance


@dataclass(slots=True)
class MatterLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one matter unit.
    Args:
        The fields mirror the documented Matter logic payload.
    Implementation Logic:
        The logic version is the main entry point for managing chemistry members,
        physical organization and matter-level weak interactions together.
    """

    _object_type: ClassVar[str] = "Matter"
    _debug_module: ClassVar[str] = "logic.matter"

    _id: str
    bChemMoleculeList: dict[str, MoleculeLogic]
    bPhyMoleculeGap: str | None = None
    bPhyMoleculeArrangement: dict[str, Any] | None = None
    bMatterIntmolInteractionList: list[MatterIntmolInteractionLogic] | None = None

    def __post_init__(self) -> None:
        """
        Function:
            Normalize physical fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The Matter logic layer normalizes the stable physical gap field when
            the object is instantiated.
        """

        self.bPhyMoleculeGap = normalize_field_value("bPhyMoleculeGap", self.bPhyMoleculeGap)
        if self.bMatterIntmolInteractionList is None:
            self.bMatterIntmolInteractionList = []
        self._log_debug(
            message="MatterLogic created.",
            context={
                "_id": self._id,
                "moleculeCount": len(self.bChemMoleculeList),
                "interactionCount": len(self.bMatterIntmolInteractionList),
            },
        )

    def toDescriptor(self) -> MatterDescriptor:
        """
        Function:
            Convert the logic matter object into a stable descriptor.
        Args:
            None.
        Returns:
            MatterDescriptor: Stable matter descriptor.
        Implementation Logic:
            Runtime logic state is excluded and nested members are individually
            translated back into stable descriptors.
        """

        descriptor = MatterDescriptor(
            _id=self._id,
            bChemMoleculeList={
                molecule_id: molecule.toDescriptor()
                for molecule_id, molecule in self.bChemMoleculeList.items()
            },
            bPhyMoleculeGap=self.bPhyMoleculeGap,
            bPhyMoleculeArrangement=deepcopy(self.bPhyMoleculeArrangement),
            bMatterIntmolInteractionList=[
                interaction.toDescriptor()
                for interaction in self.bMatterIntmolInteractionList
            ],
        )
        self._log_debug(message="MatterLogic converted to descriptor.", context={"_id": self._id})
        return descriptor

    def toCalculus(self) -> MatterCalculus:
        """
        Function:
            Convert the logic matter object into a calculus representation.
        Args:
            None.
        Returns:
            MatterCalculus: Computation-oriented matter object.
        Implementation Logic:
            Version translation routes through the descriptor representation to
            keep hash behavior centralized.
        """

        calculus = MatterCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(message="MatterLogic converted to calculus.", context={"_id": self._id})
        return calculus

    @classmethod
    def fromDescriptor(cls, descriptor: MatterDescriptor) -> "MatterLogic":
        """
        Function:
            Build a matter logic object from a descriptor.
        Args:
            descriptor: Source matter descriptor.
        Returns:
            MatterLogic: New logic object.
        Implementation Logic:
            The logic object restores molecules and matter-level interactions
            from their descriptor forms for business-layer access.
        """

        instance = cls(
            _id=descriptor._id,
            bChemMoleculeList={
                molecule_id: MoleculeLogic.fromDescriptor(molecule)
                for molecule_id, molecule in descriptor.bChemMoleculeList.items()
            },
            bPhyMoleculeGap=descriptor.bPhyMoleculeGap,
            bPhyMoleculeArrangement=deepcopy(descriptor.bPhyMoleculeArrangement),
            bMatterIntmolInteractionList=[
                MatterIntmolInteractionLogic.fromDescriptor(interaction)
                for interaction in (descriptor.bMatterIntmolInteractionList or [])
            ],
        )
        instance._log_debug(message="MatterLogic created from descriptor.", context={"_id": instance._id})
        return instance

    @classmethod
    def fromCalculus(cls, calculus: MatterCalculus) -> "MatterLogic":
        """
        Function:
            Build a matter logic object from a calculus version.
        Args:
            calculus: Source calculus object.
        Returns:
            MatterLogic: New logic object.
        Implementation Logic:
            Conversion routes through the descriptor representation to preserve
            one canonical payload path.
        """

        return cls.fromDescriptor(calculus.toDescriptor())
