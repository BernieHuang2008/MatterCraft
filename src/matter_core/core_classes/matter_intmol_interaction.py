"""MatterIntmolInteraction LDC classes for MatterCraft."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, ClassVar

from matter_core.common import MatterCalculusBase, MatterDescriptorBase, MatterLogicBase
from matter_core.common.units import normalize_field_value


@dataclass(slots=True)
class MatterIntmolInteractionDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one matter-level intermolecular interaction.
    Args:
        The fields mirror the documented MatterIntmolInteraction properties.
    Implementation Logic:
        Participants are stored as stable serializable payloads so the object can
        describe weak interactions without runtime-memory dependencies.
    """

    _object_type: ClassVar[str] = "MatterIntmolInteraction"
    _debug_module: ClassVar[str] = "descriptor.matter_intmol_interaction"

    _id: str
    bInteractionType: str
    bParticipantList: list[Any]
    bInteractionStrength: str | None = None
    bInteractionDistance: str | None = None
    bDirectionality: dict[str, Any] | None = None
    bGeometry: dict[str, Any] | None = None
    bInteractionModel: str | None = None

    def __post_init__(self) -> None:
        """
        Function:
            Normalize numeric fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Stable interaction strength and distance values are normalized at
            creation time for consistent hashing.
        """

        self.bInteractionStrength = normalize_field_value(
            "bInteractionStrength",
            self.bInteractionStrength,
        )
        self.bInteractionDistance = normalize_field_value(
            "bInteractionDistance",
            self.bInteractionDistance,
        )
        self._log_debug(
            message="MatterIntmolInteractionDescriptor created.",
            context={"_id": self._id, "interactionType": self.bInteractionType},
        )


@dataclass(slots=True)
class MatterIntmolInteractionCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one matter-level intermolecular interaction.
    Args:
        The fields mirror the first descriptor-based calculus layout.
    Implementation Logic:
        The first calculus version preserves the same stable data shape and
        leaves room for future optimized interaction models.
    """

    _object_type: ClassVar[str] = "MatterIntmolInteraction"
    _debug_module: ClassVar[str] = "calculus.matter_intmol_interaction"

    _id: str
    bInteractionType: str
    bParticipantList: list[Any]
    bInteractionStrength: str | None = None
    bInteractionDistance: str | None = None
    bDirectionality: dict[str, Any] | None = None
    bGeometry: dict[str, Any] | None = None
    bInteractionModel: str | None = None

    def toDescriptor(self) -> MatterIntmolInteractionDescriptor:
        """
        Function:
            Convert the calculus interaction into a stable descriptor.
        Args:
            None.
        Returns:
            MatterIntmolInteractionDescriptor: Stable interaction descriptor.
        Implementation Logic:
            The conversion copies the serializable interaction payload directly.
        """

        return MatterIntmolInteractionDescriptor(
            _id=self._id,
            bInteractionType=self.bInteractionType,
            bParticipantList=deepcopy(self.bParticipantList),
            bInteractionStrength=self.bInteractionStrength,
            bInteractionDistance=self.bInteractionDistance,
            bDirectionality=deepcopy(self.bDirectionality),
            bGeometry=deepcopy(self.bGeometry),
            bInteractionModel=self.bInteractionModel,
        )

    @classmethod
    def fromDescriptor(
        cls,
        descriptor: MatterIntmolInteractionDescriptor,
    ) -> "MatterIntmolInteractionCalculus":
        """
        Function:
            Build a calculus interaction object from a descriptor.
        Args:
            descriptor: Source interaction descriptor.
        Returns:
            MatterIntmolInteractionCalculus: New calculus object.
        Implementation Logic:
            The first calculus version mirrors descriptor fields directly.
        """

        instance = cls(
            _id=descriptor._id,
            bInteractionType=descriptor.bInteractionType,
            bParticipantList=deepcopy(descriptor.bParticipantList),
            bInteractionStrength=descriptor.bInteractionStrength,
            bInteractionDistance=descriptor.bInteractionDistance,
            bDirectionality=deepcopy(descriptor.bDirectionality),
            bGeometry=deepcopy(descriptor.bGeometry),
            bInteractionModel=descriptor.bInteractionModel,
        )
        instance._log_debug(
            message="MatterIntmolInteractionCalculus created from descriptor.",
            context={"_id": instance._id},
        )
        return instance


@dataclass(slots=True)
class MatterIntmolInteractionLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one matter-level intermolecular interaction.
    Args:
        The fields mirror the documented MatterIntmolInteraction payload.
    Implementation Logic:
        The logic version provides the main editing surface while keeping the
        interaction payload serializable and descriptor-friendly.
    """

    _object_type: ClassVar[str] = "MatterIntmolInteraction"
    _debug_module: ClassVar[str] = "logic.matter_intmol_interaction"

    _id: str
    bInteractionType: str
    bParticipantList: list[Any]
    bInteractionStrength: str | None = None
    bInteractionDistance: str | None = None
    bDirectionality: dict[str, Any] | None = None
    bGeometry: dict[str, Any] | None = None
    bInteractionModel: str | None = None

    def __post_init__(self) -> None:
        """
        Function:
            Normalize numeric fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Normalization keeps the logic object's stable payload aligned with
            descriptor and hash expectations.
        """

        self.bInteractionStrength = normalize_field_value(
            "bInteractionStrength",
            self.bInteractionStrength,
        )
        self.bInteractionDistance = normalize_field_value(
            "bInteractionDistance",
            self.bInteractionDistance,
        )
        self._log_debug(
            message="MatterIntmolInteractionLogic created.",
            context={"_id": self._id, "interactionType": self.bInteractionType},
        )

    def toDescriptor(self) -> MatterIntmolInteractionDescriptor:
        """
        Function:
            Convert the logic interaction into a stable descriptor.
        Args:
            None.
        Returns:
            MatterIntmolInteractionDescriptor: Stable interaction descriptor.
        Implementation Logic:
            The descriptor conversion copies the serializable interaction payload
            directly because no runtime-only references are stored here.
        """

        descriptor = MatterIntmolInteractionDescriptor(
            _id=self._id,
            bInteractionType=self.bInteractionType,
            bParticipantList=deepcopy(self.bParticipantList),
            bInteractionStrength=self.bInteractionStrength,
            bInteractionDistance=self.bInteractionDistance,
            bDirectionality=deepcopy(self.bDirectionality),
            bGeometry=deepcopy(self.bGeometry),
            bInteractionModel=self.bInteractionModel,
        )
        self._log_debug(
            message="MatterIntmolInteractionLogic converted to descriptor.",
            context={"_id": self._id},
        )
        return descriptor

    def toCalculus(self) -> MatterIntmolInteractionCalculus:
        """
        Function:
            Convert the logic interaction into a calculus representation.
        Args:
            None.
        Returns:
            MatterIntmolInteractionCalculus: Computation-oriented interaction object.
        Implementation Logic:
            Version translation routes through the canonical descriptor form.
        """

        calculus = MatterIntmolInteractionCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(
            message="MatterIntmolInteractionLogic converted to calculus.",
            context={"_id": self._id},
        )
        return calculus

    @classmethod
    def fromDescriptor(
        cls,
        descriptor: MatterIntmolInteractionDescriptor,
    ) -> "MatterIntmolInteractionLogic":
        """
        Function:
            Build a logic interaction object from a descriptor.
        Args:
            descriptor: Source interaction descriptor.
        Returns:
            MatterIntmolInteractionLogic: New logic object.
        Implementation Logic:
            The logic version restores the same stable payload so interaction
            editing starts from descriptor-defined data.
        """

        instance = cls(
            _id=descriptor._id,
            bInteractionType=descriptor.bInteractionType,
            bParticipantList=deepcopy(descriptor.bParticipantList),
            bInteractionStrength=descriptor.bInteractionStrength,
            bInteractionDistance=descriptor.bInteractionDistance,
            bDirectionality=deepcopy(descriptor.bDirectionality),
            bGeometry=deepcopy(descriptor.bGeometry),
            bInteractionModel=descriptor.bInteractionModel,
        )
        instance._log_debug(
            message="MatterIntmolInteractionLogic created from descriptor.",
            context={"_id": instance._id},
        )
        return instance

    @classmethod
    def fromCalculus(
        cls,
        calculus: MatterIntmolInteractionCalculus,
    ) -> "MatterIntmolInteractionLogic":
        """
        Function:
            Build a logic interaction object from a calculus version.
        Args:
            calculus: Source calculus object.
        Returns:
            MatterIntmolInteractionLogic: New logic object.
        Implementation Logic:
            Conversion routes through the descriptor representation to keep LDC
            behavior unified.
        """

        return cls.fromDescriptor(calculus.toDescriptor())
