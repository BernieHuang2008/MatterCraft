"""Mixture and MixtureComponent LDC classes for MatterCraft."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, ClassVar

from matter_core.common import MatterCalculusBase, MatterDescriptorBase, MatterLogicBase
from matter_core.common.units import normalize_decimal_string, normalize_field_value

from .matter import MatterCalculus, MatterDescriptor, MatterLogic


@dataclass(slots=True)
class MixtureComponentDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one mixture component.
    Args:
        The fields mirror the documented MixtureComponent stable payload.
    Implementation Logic:
        The descriptor stores stable matter identity, amount and macro-spatial
        organization without runtime parent references.
    """

    _object_type: ClassVar[str] = "MixtureComponent"
    _debug_module: ClassVar[str] = "descriptor.mixture_component"

    _id: str
    bMatter: MatterDescriptor | str
    bAmount: str
    bSpatialDistribution: str
    bContactRelation: dict[str, Any]
    aMass: str | None = None
    aVolume: str | None = None
    aMoleFraction: str | None = None
    aMassFraction: str | None = None
    aVolumeFraction: str | None = None
    aAmountConcentration: str | None = None
    aMassConcentration: str | None = None

    def __post_init__(self) -> None:
        """
        Function:
            Normalize stable numeric component fields and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Amount is a documented normalized quantity and derived fraction
            fields stay stable when they are already available.
        """

        self.bAmount = normalize_field_value("bAmount", self.bAmount)
        self._log_debug(
            message="MixtureComponentDescriptor created.",
            context={"_id": self._id, "spatialDistribution": self.bSpatialDistribution},
        )


@dataclass(slots=True)
class MixtureComponentCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one mixture component.
    Args:
        The fields mirror the first descriptor-based calculus layout.
    Implementation Logic:
        The first calculus version preserves the same stable data shape while
        reserving a layer for future fast concentration calculations.
    """

    _object_type: ClassVar[str] = "MixtureComponent"
    _debug_module: ClassVar[str] = "calculus.mixture_component"

    _id: str
    bMatter: MatterCalculus | MatterDescriptor | str
    bAmount: str
    bSpatialDistribution: str
    bContactRelation: dict[str, Any]
    aMass: str | None = None
    aVolume: str | None = None
    aMoleFraction: str | None = None
    aMassFraction: str | None = None
    aVolumeFraction: str | None = None
    aAmountConcentration: str | None = None
    aMassConcentration: str | None = None

    def toDescriptor(self) -> MixtureComponentDescriptor:
        """
        Function:
            Convert the calculus mixture component into a stable descriptor.
        Args:
            None.
        Returns:
            MixtureComponentDescriptor: Stable component descriptor.
        Implementation Logic:
            Matter payloads are converted back into descriptors if a calculus
            object is present; otherwise stable references are copied through.
        """

        if isinstance(self.bMatter, MatterCalculus):
            descriptor_matter: MatterDescriptor | str = self.bMatter.toDescriptor()
        else:
            descriptor_matter = deepcopy(self.bMatter)
        return MixtureComponentDescriptor(
            _id=self._id,
            bMatter=descriptor_matter,
            bAmount=self.bAmount,
            bSpatialDistribution=self.bSpatialDistribution,
            bContactRelation=deepcopy(self.bContactRelation),
            aMass=self.aMass,
            aVolume=self.aVolume,
            aMoleFraction=self.aMoleFraction,
            aMassFraction=self.aMassFraction,
            aVolumeFraction=self.aVolumeFraction,
            aAmountConcentration=self.aAmountConcentration,
            aMassConcentration=self.aMassConcentration,
        )

    @classmethod
    def fromDescriptor(
        cls,
        descriptor: MixtureComponentDescriptor,
    ) -> "MixtureComponentCalculus":
        """
        Function:
            Build a mixture-component calculus object from a descriptor.
        Args:
            descriptor: Source component descriptor.
        Returns:
            MixtureComponentCalculus: New calculus object.
        Implementation Logic:
            Nested Matter descriptors are converted into Matter calculus objects
            when present, while stable string references pass through unchanged.
        """

        if isinstance(descriptor.bMatter, MatterDescriptor):
            calculus_matter: MatterCalculus | MatterDescriptor | str = MatterCalculus.fromDescriptor(
                descriptor.bMatter
            )
        else:
            calculus_matter = descriptor.bMatter
        instance = cls(
            _id=descriptor._id,
            bMatter=calculus_matter,
            bAmount=descriptor.bAmount,
            bSpatialDistribution=descriptor.bSpatialDistribution,
            bContactRelation=deepcopy(descriptor.bContactRelation),
            aMass=descriptor.aMass,
            aVolume=descriptor.aVolume,
            aMoleFraction=descriptor.aMoleFraction,
            aMassFraction=descriptor.aMassFraction,
            aVolumeFraction=descriptor.aVolumeFraction,
            aAmountConcentration=descriptor.aAmountConcentration,
            aMassConcentration=descriptor.aMassConcentration,
        )
        instance._log_debug(
            message="MixtureComponentCalculus created from descriptor.",
            context={"_id": instance._id},
        )
        return instance


@dataclass(slots=True)
class MixtureComponentLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one mixture component.
    Args:
        The fields mirror the documented MixtureComponent logic payload.
    Implementation Logic:
        The logic version holds the business-level component definition and
        derives mixture fractions when linked to a runtime parent mixture.
    """

    _object_type: ClassVar[str] = "MixtureComponent"
    _debug_module: ClassVar[str] = "logic.mixture_component"

    _id: str
    bMatter: MatterLogic | MatterDescriptor | str
    bAmount: str
    bSpatialDistribution: str
    bContactRelation: dict[str, Any]
    aMass: str | None = None
    aVolume: str | None = None
    aMoleFraction: str | None = None
    aMassFraction: str | None = None
    aVolumeFraction: str | None = None
    aAmountConcentration: str | None = None
    aMassConcentration: str | None = None
    rParentMixture: object | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """
        Function:
            Normalize stable amount input and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            Component amount is normalized immediately and the object announces
            its creation through the unified debug module.
        """

        self.bAmount = normalize_field_value("bAmount", self.bAmount)
        self._log_debug(
            message="MixtureComponentLogic created.",
            context={"_id": self._id, "spatialDistribution": self.bSpatialDistribution},
        )

    def refreshDerivedValues(self) -> None:
        """
        Function:
            Refresh mixture-derived fraction values from the runtime parent mixture.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The first implementation derives mole fractions from total amount
            when the component belongs to a runtime mixture; mass and volume
            fields remain optional placeholders until later chemistry models.
        """

        if self.rParentMixture is None:
            self.aMoleFraction = None
            return
        component_list = getattr(self.rParentMixture, "bMixtureComponentList", [])
        total_amount = sum(Decimal(str(component.bAmount)) for component in component_list)
        if total_amount == 0:
            self.aMoleFraction = None
            return
        self.aMoleFraction = normalize_decimal_string(
            value=Decimal(str(self.bAmount)) / total_amount,
            quantum="1e-12",
        )

    def toDescriptor(self) -> MixtureComponentDescriptor:
        """
        Function:
            Convert the logic mixture component into a stable descriptor.
        Args:
            None.
        Returns:
            MixtureComponentDescriptor: Stable component descriptor.
        Implementation Logic:
            Runtime parent references are excluded and nested Matter logic
            objects are converted back into stable descriptors.
        """

        if isinstance(self.bMatter, MatterLogic):
            descriptor_matter: MatterDescriptor | str = self.bMatter.toDescriptor()
        else:
            descriptor_matter = deepcopy(self.bMatter)
        descriptor = MixtureComponentDescriptor(
            _id=self._id,
            bMatter=descriptor_matter,
            bAmount=self.bAmount,
            bSpatialDistribution=self.bSpatialDistribution,
            bContactRelation=deepcopy(self.bContactRelation),
            aMass=self.aMass,
            aVolume=self.aVolume,
            aMoleFraction=self.aMoleFraction,
            aMassFraction=self.aMassFraction,
            aVolumeFraction=self.aVolumeFraction,
            aAmountConcentration=self.aAmountConcentration,
            aMassConcentration=self.aMassConcentration,
        )
        self._log_debug(message="MixtureComponentLogic converted to descriptor.", context={"_id": self._id})
        return descriptor

    def toCalculus(self) -> MixtureComponentCalculus:
        """
        Function:
            Convert the logic mixture component into a calculus representation.
        Args:
            None.
        Returns:
            MixtureComponentCalculus: Computation-oriented component object.
        Implementation Logic:
            Version translation routes through the stable descriptor form.
        """

        calculus = MixtureComponentCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(message="MixtureComponentLogic converted to calculus.", context={"_id": self._id})
        return calculus

    @classmethod
    def fromDescriptor(cls, descriptor: MixtureComponentDescriptor) -> "MixtureComponentLogic":
        """
        Function:
            Build a mixture-component logic object from a descriptor.
        Args:
            descriptor: Source component descriptor.
        Returns:
            MixtureComponentLogic: New logic object.
        Implementation Logic:
            Nested Matter descriptors are restored into Matter logic objects when
            available, while stable string references pass through.
        """

        if isinstance(descriptor.bMatter, MatterDescriptor):
            logic_matter: MatterLogic | MatterDescriptor | str = MatterLogic.fromDescriptor(
                descriptor.bMatter
            )
        else:
            logic_matter = descriptor.bMatter
        instance = cls(
            _id=descriptor._id,
            bMatter=logic_matter,
            bAmount=descriptor.bAmount,
            bSpatialDistribution=descriptor.bSpatialDistribution,
            bContactRelation=deepcopy(descriptor.bContactRelation),
            aMass=descriptor.aMass,
            aVolume=descriptor.aVolume,
            aMoleFraction=descriptor.aMoleFraction,
            aMassFraction=descriptor.aMassFraction,
            aVolumeFraction=descriptor.aVolumeFraction,
            aAmountConcentration=descriptor.aAmountConcentration,
            aMassConcentration=descriptor.aMassConcentration,
        )
        instance._log_debug(
            message="MixtureComponentLogic created from descriptor.",
            context={"_id": instance._id},
        )
        return instance

    @classmethod
    def fromCalculus(cls, calculus: MixtureComponentCalculus) -> "MixtureComponentLogic":
        """
        Function:
            Build a mixture-component logic object from a calculus version.
        Args:
            calculus: Source calculus object.
        Returns:
            MixtureComponentLogic: New logic object.
        Implementation Logic:
            Conversion routes through the descriptor representation so one
            canonical payload remains authoritative.
        """

        return cls.fromDescriptor(calculus.toDescriptor())


@dataclass(slots=True)
class MixtureDescriptor(MatterDescriptorBase):
    """
    Function:
        Store the stable descriptor representation of one mixture.
    Args:
        _id: Stable instance ID.
        bMixtureType: Mixture macro-type name.
        bMixtureTypeProperty: Serializable type-property payload.
        bMixtureComponentList: Stable component collection.
    Implementation Logic:
        The descriptor keeps only the stable macro-composition information that
        defines a mixture.
    """

    _object_type: ClassVar[str] = "Mixture"
    _debug_module: ClassVar[str] = "descriptor.mixture"

    _id: str
    bMixtureType: str
    bMixtureTypeProperty: dict[str, Any]
    bMixtureComponentList: list[MixtureComponentDescriptor]

    def __post_init__(self) -> None:
        """
        Function:
            Emit a debug event after mixture descriptor creation.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The event includes component count because that is the key summary
            for the first mixture-layer implementation.
        """

        self._log_debug(
            message="MixtureDescriptor created.",
            context={"_id": self._id, "componentCount": len(self.bMixtureComponentList)},
        )


@dataclass(slots=True)
class MixtureCalculus(MatterCalculusBase):
    """
    Function:
        Store the computation-oriented representation of one mixture.
    Args:
        The fields mirror the first descriptor-based mixture calculus layout.
    Implementation Logic:
        The first calculus version preserves stable structure and leaves room for
        future optimized concentration and transport calculations.
    """

    _object_type: ClassVar[str] = "Mixture"
    _debug_module: ClassVar[str] = "calculus.mixture"

    _id: str
    bMixtureType: str
    bMixtureTypeProperty: dict[str, Any]
    bMixtureComponentList: list[MixtureComponentCalculus]

    def toDescriptor(self) -> MixtureDescriptor:
        """
        Function:
            Convert the calculus mixture into a stable descriptor.
        Args:
            None.
        Returns:
            MixtureDescriptor: Stable mixture descriptor.
        Implementation Logic:
            Nested components are converted back into descriptors while the
            serializable type-property payload is copied directly.
        """

        return MixtureDescriptor(
            _id=self._id,
            bMixtureType=self.bMixtureType,
            bMixtureTypeProperty=deepcopy(self.bMixtureTypeProperty),
            bMixtureComponentList=[component.toDescriptor() for component in self.bMixtureComponentList],
        )

    @classmethod
    def fromDescriptor(cls, descriptor: MixtureDescriptor) -> "MixtureCalculus":
        """
        Function:
            Build a mixture calculus object from a descriptor.
        Args:
            descriptor: Source mixture descriptor.
        Returns:
            MixtureCalculus: New calculus object.
        Implementation Logic:
            Component descriptors are translated into calculus objects one by
            one, preserving descriptor order for now.
        """

        instance = cls(
            _id=descriptor._id,
            bMixtureType=descriptor.bMixtureType,
            bMixtureTypeProperty=deepcopy(descriptor.bMixtureTypeProperty),
            bMixtureComponentList=[
                MixtureComponentCalculus.fromDescriptor(component)
                for component in descriptor.bMixtureComponentList
            ],
        )
        instance._log_debug(message="MixtureCalculus created from descriptor.", context={"_id": instance._id})
        return instance


@dataclass(slots=True)
class MixtureLogic(MatterLogicBase):
    """
    Function:
        Store the main business-logic representation of one mixture.
    Args:
        The fields mirror the documented Mixture logic payload.
    Implementation Logic:
        The logic layer manages runtime component ownership and derived mixture
        fractions while staying aligned with the stable descriptor shape.
    """

    _object_type: ClassVar[str] = "Mixture"
    _debug_module: ClassVar[str] = "logic.mixture"

    _id: str
    bMixtureType: str
    bMixtureTypeProperty: dict[str, Any]
    bMixtureComponentList: list[MixtureComponentLogic]

    def __post_init__(self) -> None:
        """
        Function:
            Attach runtime parent links, refresh fractions and emit a debug event.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The mixture owns its component membership, so runtime parent links
            and derived mole fractions are refreshed immediately.
        """

        for component in self.bMixtureComponentList:
            component.rParentMixture = self
        self.refreshDerivedValues()
        self._log_debug(
            message="MixtureLogic created.",
            context={"_id": self._id, "componentCount": len(self.bMixtureComponentList)},
        )

    def refreshDerivedValues(self) -> None:
        """
        Function:
            Refresh derived values on every component currently in the mixture.
        Args:
            None.
        Returns:
            None.
        Implementation Logic:
            The first mixture implementation delegates component-specific
            derived-value computation to each component object.
        """

        for component in self.bMixtureComponentList:
            component.rParentMixture = self
            component.refreshDerivedValues()

    def addComponent(self, component: MixtureComponentLogic) -> None:
        """
        Function:
            Add one component to the mixture.
        Args:
            component: Component logic object to add.
        Returns:
            None.
        Implementation Logic:
            The mixture updates runtime ownership and derived values after every
            structural mutation.
        """

        component.rParentMixture = self
        self.bMixtureComponentList.append(component)
        self.refreshDerivedValues()
        self._log_debug(message="Component added to mixture.", context={"mixtureId": self._id, "componentId": component._id})

    def toDescriptor(self) -> MixtureDescriptor:
        """
        Function:
            Convert the logic mixture into a stable descriptor.
        Args:
            None.
        Returns:
            MixtureDescriptor: Stable mixture descriptor.
        Implementation Logic:
            Runtime parent links are excluded while nested components are
            individually translated into stable descriptors.
        """

        descriptor = MixtureDescriptor(
            _id=self._id,
            bMixtureType=self.bMixtureType,
            bMixtureTypeProperty=deepcopy(self.bMixtureTypeProperty),
            bMixtureComponentList=[component.toDescriptor() for component in self.bMixtureComponentList],
        )
        self._log_debug(message="MixtureLogic converted to descriptor.", context={"_id": self._id})
        return descriptor

    def toCalculus(self) -> MixtureCalculus:
        """
        Function:
            Convert the logic mixture into a calculus representation.
        Args:
            None.
        Returns:
            MixtureCalculus: Computation-oriented mixture object.
        Implementation Logic:
            Version translation routes through the canonical descriptor form.
        """

        calculus = MixtureCalculus.fromDescriptor(self.toDescriptor())
        self._log_debug(message="MixtureLogic converted to calculus.", context={"_id": self._id})
        return calculus

    @classmethod
    def fromDescriptor(cls, descriptor: MixtureDescriptor) -> "MixtureLogic":
        """
        Function:
            Build a mixture logic object from a descriptor.
        Args:
            descriptor: Source mixture descriptor.
        Returns:
            MixtureLogic: New logic object.
        Implementation Logic:
            Component descriptors are restored into logic objects and then linked
            back to the runtime parent mixture during initialization.
        """

        instance = cls(
            _id=descriptor._id,
            bMixtureType=descriptor.bMixtureType,
            bMixtureTypeProperty=deepcopy(descriptor.bMixtureTypeProperty),
            bMixtureComponentList=[
                MixtureComponentLogic.fromDescriptor(component)
                for component in descriptor.bMixtureComponentList
            ],
        )
        instance._log_debug(message="MixtureLogic created from descriptor.", context={"_id": instance._id})
        return instance

    @classmethod
    def fromCalculus(cls, calculus: MixtureCalculus) -> "MixtureLogic":
        """
        Function:
            Build a mixture logic object from a calculus version.
        Args:
            calculus: Source calculus object.
        Returns:
            MixtureLogic: New logic object.
        Implementation Logic:
            Conversion routes through the descriptor representation so one
            canonical mixture payload remains authoritative.
        """

        return cls.fromDescriptor(calculus.toDescriptor())
