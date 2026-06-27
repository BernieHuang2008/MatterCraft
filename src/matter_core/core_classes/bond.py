"""Bond LDC classes for MatterCraft."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import ClassVar

from matter_core.common import MatterCalculusBase, MatterDescriptorBase, MatterLogicBase
from matter_core.common.units import normalize_field_value

from .atom import AtomCalculus, AtomDescriptor, AtomLogic


@dataclass(slots=True)
class BondDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one bond.
    Args:
        The fields mirror the documented Bond basic properties.
    Implementation Logic:
        The descriptor keeps stable bond-defining data only, excluding runtime
        parent references from canonical storage and hashing.
    """

    _object_type: ClassVar[str] = "Bond"
    _debug_module: ClassVar[str] = "descriptor.bond"

    _id: str
    bAtomList: list[AtomDescriptor]
    bBondType: str
    bBondOrder: str | None = None
    bElectronCount: int | None = None
    bIsDelocalized: bool = False
    bBondEnergy: str | None = None
    bBondLength: str | None = None
    bPolarity: str | None = None
    bMetalBondModel: str | None = None
    bDelocalizedElectronCount: int | None = None
    bCoordinationNumber: int | None = None
    bLatticeType: str | None = None
    bMetallicBondStrength: str | None = None

    def __post_init__(self) -> None:
        """
        Function:
            Normalize numeric fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Normalization keeps stable numeric fields hash-safe from the moment
            the descriptor is created.
        """

        self.bBondOrder = normalize_field_value("bBondOrder", self.bBondOrder)
        self.bBondEnergy = normalize_field_value("bBondEnergy", self.bBondEnergy)
        self.bBondLength = normalize_field_value("bBondLength", self.bBondLength)
        self.bPolarity = normalize_field_value("bPolarity", self.bPolarity)
        self.bMetallicBondStrength = normalize_field_value(
            "bMetallicBondStrength",
            self.bMetallicBondStrength,
        )
        self._log_debug(message="BondDescriptor created.", context={"_id": self._id, "bondType": self.bBondType})


@dataclass(slots=True)
class BondCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one bond.
    Args:
        The fields mirror the first descriptor-based calculus layout.
    Implementation Logic:
        The first calculus version stays close to the descriptor while keeping a
        stable surface for future optimized internal layouts.
    """

    _object_type: ClassVar[str] = "Bond"
    _debug_module: ClassVar[str] = "calculus.bond"

    _id: str
    bAtomList: list[AtomCalculus]
    bBondType: str
    bBondOrder: str | None = None
    bElectronCount: int | None = None
    bIsDelocalized: bool = False
    bBondEnergy: str | None = None
    bBondLength: str | None = None
    bPolarity: str | None = None
    bMetalBondModel: str | None = None
    bDelocalizedElectronCount: int | None = None
    bCoordinationNumber: int | None = None
    bLatticeType: str | None = None
    bMetallicBondStrength: str | None = None

    def toDescriptor(self) -> BondDescriptor:
        """
        Function:
            Convert the calculus bond into a stable descriptor.
        Args:
            None.
        Returns:
            BondDescriptor: Stable bond descriptor.
        Implementation Logic:
            Nested atom members are converted back into descriptors before the
            outer bond descriptor is assembled.
        """

        return BondDescriptor(
            _id=self._id,
            bAtomList=[atom.toDescriptor() for atom in self.bAtomList],
            bBondType=self.bBondType,
            bBondOrder=self.bBondOrder,
            bElectronCount=self.bElectronCount,
            bIsDelocalized=self.bIsDelocalized,
            bBondEnergy=self.bBondEnergy,
            bBondLength=self.bBondLength,
            bPolarity=self.bPolarity,
            bMetalBondModel=self.bMetalBondModel,
            bDelocalizedElectronCount=self.bDelocalizedElectronCount,
            bCoordinationNumber=self.bCoordinationNumber,
            bLatticeType=self.bLatticeType,
            bMetallicBondStrength=self.bMetallicBondStrength,
        )

    @classmethod
    def fromDescriptor(cls, descriptor: BondDescriptor) -> "BondCalculus":
        """
        Function:
            Build a bond calculus object from a descriptor.
        Args:
            descriptor: Source bond descriptor.
        Returns:
            BondCalculus: New calculus object.
        Implementation Logic:
            Nested atom descriptors are converted into their calculus versions so
            later performance-oriented work has a dedicated layer.
        """

        instance = cls(
            _id=descriptor._id,
            bAtomList=[AtomCalculus.fromDescriptor(atom) for atom in descriptor.bAtomList],
            bBondType=descriptor.bBondType,
            bBondOrder=descriptor.bBondOrder,
            bElectronCount=descriptor.bElectronCount,
            bIsDelocalized=descriptor.bIsDelocalized,
            bBondEnergy=descriptor.bBondEnergy,
            bBondLength=descriptor.bBondLength,
            bPolarity=descriptor.bPolarity,
            bMetalBondModel=descriptor.bMetalBondModel,
            bDelocalizedElectronCount=descriptor.bDelocalizedElectronCount,
            bCoordinationNumber=descriptor.bCoordinationNumber,
            bLatticeType=descriptor.bLatticeType,
            bMetallicBondStrength=descriptor.bMetallicBondStrength,
        )
        instance._log_debug(message="BondCalculus created from descriptor.", context={"_id": instance._id})
        return instance


@dataclass(slots=True)
class BondLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one bond.
    Args:
        The fields mirror the documented Bond logic payload.
    Implementation Logic:
        The logic version keeps stable bond properties plus runtime-only parent
        references used by higher-level molecular editing workflows.
    """

    _object_type: ClassVar[str] = "Bond"
    _debug_module: ClassVar[str] = "logic.bond"

    _id: str
    bAtomList: list[AtomLogic]
    bBondType: str
    bBondOrder: str | None = None
    bElectronCount: int | None = None
    bIsDelocalized: bool = False
    bBondEnergy: str | None = None
    bBondLength: str | None = None
    bPolarity: str | None = None
    bMetalBondModel: str | None = None
    bDelocalizedElectronCount: int | None = None
    bCoordinationNumber: int | None = None
    bLatticeType: str | None = None
    bMetallicBondStrength: str | None = None
    rParentMolecule: object | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """
        Function:
            Normalize numeric bond fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The logic layer normalizes stable numeric payloads immediately so
            later conversions do not need to repeat that work.
        """

        self.bBondOrder = normalize_field_value("bBondOrder", self.bBondOrder)
        self.bBondEnergy = normalize_field_value("bBondEnergy", self.bBondEnergy)
        self.bBondLength = normalize_field_value("bBondLength", self.bBondLength)
        self.bPolarity = normalize_field_value("bPolarity", self.bPolarity)
        self.bMetallicBondStrength = normalize_field_value(
            "bMetallicBondStrength",
            self.bMetallicBondStrength,
        )
        self._log_debug(message="BondLogic created.", context={"_id": self._id, "bondType": self.bBondType})

    def toDescriptor(self) -> BondDescriptor:
        """
        Function:
            Convert the logic bond into a stable descriptor.
        Args:
            None.
        Returns:
            BondDescriptor: Stable bond descriptor.
        Implementation Logic:
            Runtime parent references are intentionally excluded from descriptor
            conversion to match the documented hash boundary.
        """

        descriptor = BondDescriptor(
            _id=self._id,
            bAtomList=[atom.toDescriptor() for atom in self.bAtomList],
            bBondType=self.bBondType,
            bBondOrder=self.bBondOrder,
            bElectronCount=self.bElectronCount,
            bIsDelocalized=self.bIsDelocalized,
            bBondEnergy=self.bBondEnergy,
            bBondLength=self.bBondLength,
            bPolarity=self.bPolarity,
            bMetalBondModel=self.bMetalBondModel,
            bDelocalizedElectronCount=self.bDelocalizedElectronCount,
            bCoordinationNumber=self.bCoordinationNumber,
            bLatticeType=self.bLatticeType,
            bMetallicBondStrength=self.bMetallicBondStrength,
        )
        self._log_debug(message="BondLogic converted to descriptor.", context={"_id": self._id})
        return descriptor

    def toCalculus(self) -> BondCalculus:
        """
        Function:
            Convert the logic bond into a calculus representation.
        Args:
            None.
        Returns:
            BondCalculus: Computation-oriented bond.
        Implementation Logic:
            The logic layer owns LDC translation and reuses descriptor-based
            conversion to keep canonical behavior aligned.
        """

        calculus = BondCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(message="BondLogic converted to calculus.", context={"_id": self._id})
        return calculus

    @classmethod
    def fromDescriptor(cls, descriptor: BondDescriptor) -> "BondLogic":
        """
        Function:
            Build a bond logic object from a descriptor.
        Args:
            descriptor: Source bond descriptor.
        Returns:
            BondLogic: New logic object.
        Implementation Logic:
            Nested atom descriptors are converted into logic objects and the
            runtime parent reference is left unset.
        """

        instance = cls(
            _id=descriptor._id,
            bAtomList=[AtomLogic.fromDescriptor(atom) for atom in descriptor.bAtomList],
            bBondType=descriptor.bBondType,
            bBondOrder=descriptor.bBondOrder,
            bElectronCount=descriptor.bElectronCount,
            bIsDelocalized=descriptor.bIsDelocalized,
            bBondEnergy=descriptor.bBondEnergy,
            bBondLength=descriptor.bBondLength,
            bPolarity=descriptor.bPolarity,
            bMetalBondModel=descriptor.bMetalBondModel,
            bDelocalizedElectronCount=descriptor.bDelocalizedElectronCount,
            bCoordinationNumber=descriptor.bCoordinationNumber,
            bLatticeType=descriptor.bLatticeType,
            bMetallicBondStrength=descriptor.bMetallicBondStrength,
            rParentMolecule=None,
        )
        instance._log_debug(message="BondLogic created from descriptor.", context={"_id": instance._id})
        return instance

    @classmethod
    def fromCalculus(cls, calculus: BondCalculus) -> "BondLogic":
        """
        Function:
            Build a bond logic object from a calculus version.
        Args:
            calculus: Source calculus object.
        Returns:
            BondLogic: New logic object.
        Implementation Logic:
            Conversion routes back through the descriptor representation so one
            canonical payload remains authoritative.
        """

        return cls.fromDescriptor(calculus.toDescriptor())
