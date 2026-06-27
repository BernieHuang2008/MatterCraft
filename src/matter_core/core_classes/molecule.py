"""Molecule LDC classes for MatterCraft."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from matter_core.common import MatterCalculusBase, MatterDescriptorBase, MatterLogicBase

from .atom import AtomCalculus, AtomDescriptor, AtomLogic
from .bond import BondCalculus, BondDescriptor, BondLogic


@dataclass(slots=True)
class MoleculeDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one molecule.
    Args:
        _id: Stable instance ID.
        bAtomList: Atom mapping keyed by atom ID.
        bBondList: Bond mapping keyed by bond ID.
    Implementation Logic:
        The descriptor keeps the stable structural members of the molecule and
        preserves ID-keyed maps for direct object lookup.
    """

    _object_type: ClassVar[str] = "Molecule"
    _debug_module: ClassVar[str] = "descriptor.molecule"

    _id: str
    bAtomList: dict[str, AtomDescriptor]
    bBondList: dict[str, BondDescriptor]

    def __post_init__(self) -> None:
        """
        Function:
            Emit a debug event after molecule descriptor creation.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The event records the current atom and bond counts for structural
            tracing in the debug window.
        """

        self._log_debug(
            message="MoleculeDescriptor created.",
            context={"_id": self._id, "atomCount": len(self.bAtomList), "bondCount": len(self.bBondList)},
        )


@dataclass(slots=True)
class MoleculeCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one molecule.
    Args:
        _id: Stable instance ID.
        bAtomList: Atom calculus mapping keyed by atom ID.
        bBondList: Bond calculus mapping keyed by bond ID.
    Implementation Logic:
        The first calculus version mirrors the stable structure while providing
        a dedicated layer for future optimized adjacency structures.
    """

    _object_type: ClassVar[str] = "Molecule"
    _debug_module: ClassVar[str] = "calculus.molecule"

    _id: str
    bAtomList: dict[str, AtomCalculus]
    bBondList: dict[str, BondCalculus]

    def toDescriptor(self) -> MoleculeDescriptor:
        """
        Function:
            Convert the calculus molecule into a stable descriptor.
        Args:
            None.
        Returns:
            MoleculeDescriptor: Stable molecule descriptor.
        Implementation Logic:
            Nested members are converted back into descriptors while preserving
            the documented ID-keyed collection structure.
        """

        return MoleculeDescriptor(
            _id=self._id,
            bAtomList={atom_id: atom.toDescriptor() for atom_id, atom in self.bAtomList.items()},
            bBondList={bond_id: bond.toDescriptor() for bond_id, bond in self.bBondList.items()},
        )

    @classmethod
    def fromDescriptor(cls, descriptor: MoleculeDescriptor) -> "MoleculeCalculus":
        """
        Function:
            Build a molecule calculus object from a descriptor.
        Args:
            descriptor: Source molecule descriptor.
        Returns:
            MoleculeCalculus: New calculus object.
        Implementation Logic:
            Atom and bond members are individually converted into their calculus
            versions so the molecule calculus layer can evolve independently.
        """

        instance = cls(
            _id=descriptor._id,
            bAtomList={atom_id: AtomCalculus.fromDescriptor(atom) for atom_id, atom in descriptor.bAtomList.items()},
            bBondList={bond_id: BondCalculus.fromDescriptor(bond) for bond_id, bond in descriptor.bBondList.items()},
        )
        instance._log_debug(message="MoleculeCalculus created from descriptor.", context={"_id": instance._id})
        return instance


@dataclass(slots=True)
class MoleculeLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one molecule.
    Args:
        _id: Stable instance ID.
        bAtomList: Atom mapping keyed by atom ID.
        bBondList: Bond mapping keyed by bond ID.
    Implementation Logic:
        The logic layer manages molecule editing workflows and keeps runtime
        parent references on nested bonds synchronized.
    """

    _object_type: ClassVar[str] = "Molecule"
    _debug_module: ClassVar[str] = "logic.molecule"

    _id: str
    bAtomList: dict[str, AtomLogic]
    bBondList: dict[str, BondLogic]

    def __post_init__(self) -> None:
        """
        Function:
            Synchronize nested runtime references and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Bonds gain the current molecule as their runtime parent so later
            logic-layer traversal does not need external repair code.
        """

        for bond in self.bBondList.values():
            bond.rParentMolecule = self
        self._log_debug(
            message="MoleculeLogic created.",
            context={"_id": self._id, "atomCount": len(self.bAtomList), "bondCount": len(self.bBondList)},
        )

    def addBond(self, bond: BondLogic) -> None:
        """
        Function:
            Add a bond to the molecule by its stable bond ID.
        Args:
            bond: Bond logic object to add.
        Returns:
            None.
        Implementation Logic:
            The molecule owns bond membership and updates the bond runtime parent
            reference as part of the insertion operation.
        """

        bond.rParentMolecule = self
        self.bBondList[bond._id] = bond
        self._log_debug(message="Bond added to molecule.", context={"moleculeId": self._id, "bondId": bond._id})

    def removeBond(self, bond_id: str) -> BondLogic:
        """
        Function:
            Remove one bond from the molecule.
        Args:
            bond_id: Stable bond ID to remove.
        Returns:
            BondLogic: Removed bond object.
        Implementation Logic:
            The method detaches the runtime parent reference and returns the
            removed bond for higher-level workflow handling.
        """

        bond = self.bBondList.pop(bond_id)
        bond.rParentMolecule = None
        self._log_debug(message="Bond removed from molecule.", context={"moleculeId": self._id, "bondId": bond_id})
        return bond

    def findBondsByAtom(self, atom_id: str) -> list[BondLogic]:
        """
        Function:
            Return all bonds that include one atom ID.
        Args:
            atom_id: Stable atom ID to match.
        Returns:
            list[BondLogic]: Matching bond list.
        Implementation Logic:
            The first implementation performs a straightforward scan over the
            existing bond collection.
        """

        return [
            bond
            for bond in self.bBondList.values()
            if any(atom._id == atom_id for atom in bond.bAtomList)
        ]

    def findNeighborAtoms(self, atom_id: str) -> list[AtomLogic]:
        """
        Function:
            Return atoms directly connected to the given atom ID.
        Args:
            atom_id: Stable atom ID to inspect.
        Returns:
            list[AtomLogic]: Neighbor atom list.
        Implementation Logic:
            Neighbor discovery walks the existing bond list and collects the
            opposite-side atoms for each matching bond.
        """

        neighbors: dict[str, AtomLogic] = {}
        for bond in self.findBondsByAtom(atom_id):
            for atom in bond.bAtomList:
                if atom._id != atom_id:
                    neighbors[atom._id] = atom
        return list(neighbors.values())

    def toDescriptor(self) -> MoleculeDescriptor:
        """
        Function:
            Convert the logic molecule into a stable descriptor.
        Args:
            None.
        Returns:
            MoleculeDescriptor: Stable molecule descriptor.
        Implementation Logic:
            Atom and bond members are converted individually while runtime-only
            links remain excluded from the descriptor payload.
        """

        descriptor = MoleculeDescriptor(
            _id=self._id,
            bAtomList={atom_id: atom.toDescriptor() for atom_id, atom in self.bAtomList.items()},
            bBondList={bond_id: bond.toDescriptor() for bond_id, bond in self.bBondList.items()},
        )
        self._log_debug(message="MoleculeLogic converted to descriptor.", context={"_id": self._id})
        return descriptor

    def toCalculus(self) -> MoleculeCalculus:
        """
        Function:
            Convert the logic molecule into a calculus representation.
        Args:
            None.
        Returns:
            MoleculeCalculus: Computation-oriented molecule.
        Implementation Logic:
            The conversion reuses the canonical descriptor form before producing
            the first calculus-layer representation.
        """

        calculus = MoleculeCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(message="MoleculeLogic converted to calculus.", context={"_id": self._id})
        return calculus

    @classmethod
    def fromDescriptor(cls, descriptor: MoleculeDescriptor) -> "MoleculeLogic":
        """
        Function:
            Build a molecule logic object from a descriptor.
        Args:
            descriptor: Source molecule descriptor.
        Returns:
            MoleculeLogic: New logic object.
        Implementation Logic:
            Nested atom and bond members are restored into logic objects and the
            resulting molecule synchronizes runtime parent references.
        """

        instance = cls(
            _id=descriptor._id,
            bAtomList={atom_id: AtomLogic.fromDescriptor(atom) for atom_id, atom in descriptor.bAtomList.items()},
            bBondList={bond_id: BondLogic.fromDescriptor(bond) for bond_id, bond in descriptor.bBondList.items()},
        )
        instance._log_debug(message="MoleculeLogic created from descriptor.", context={"_id": instance._id})
        return instance

    @classmethod
    def fromCalculus(cls, calculus: MoleculeCalculus) -> "MoleculeLogic":
        """
        Function:
            Build a molecule logic object from a calculus version.
        Args:
            calculus: Source molecule calculus object.
        Returns:
            MoleculeLogic: New logic object.
        Implementation Logic:
            Version translation routes through the descriptor representation so
            hash consistency remains centralized.
        """

        return cls.fromDescriptor(calculus.toDescriptor())
