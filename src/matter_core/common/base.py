"""Common LDC base classes for matter core objects."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, ClassVar

from debug_module import log

from .hash_utils import build_object_hash


class MatterCoreBase:
    """
    Function:
        Provide shared debug and hash behavior for matter core objects.
    Args:
        None.
    Implementation Logic:
        Concrete descriptor, logic and calculus classes inherit the same object
        hash and debug snapshot behavior so LDC versions stay consistent.
    """

    _object_type: ClassVar[str] = "MatterCoreObject"
    _debug_module: ClassVar[str] = "logic.core"

    def hash(self) -> str:
        """
        Function:
            Return the canonical property hash of the current object.
        Args:
            None.
        Returns:
            str: Lowercase SHA-256 digest.
        Implementation Logic:
            Logic and calculus versions first convert themselves to descriptor,
            then reuse the shared canonical descriptor hash implementation.
        """

        return build_object_hash(object_type=self._object_type, descriptor=self.toDescriptor())

    def debugSnapshot(self) -> dict[str, Any]:
        """
        Function:
            Produce a structured debug snapshot of the current object.
        Args:
            None.
        Returns:
            dict[str, Any]: Debug snapshot payload.
        Implementation Logic:
            The snapshot exposes object identity, hash and descriptor contents so
            the debug window can inspect any core object consistently.
        """

        descriptor = self.toDescriptor()
        descriptor_payload: Any
        if is_dataclass(descriptor):
            descriptor_payload = asdict(descriptor)
        else:
            descriptor_payload = vars(descriptor)
        return {
            "objectType": self._object_type,
            "_id": getattr(self, "_id", None),
            "hash": self.hash(),
            "descriptor": descriptor_payload,
        }

    def _log_debug(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        level: str = "debug",
    ) -> None:
        """
        Function:
            Emit one structured debug event for the current object.
        Args:
            message: Human-readable debug message.
            context: Optional structured context payload.
            level: Log level name.
        Returns:
            None.
        Implementation Logic:
            A small helper keeps core-class instrumentation uniform and ensures
            every debug message flows through the central debug module.
        """

        log(level=level, module=self._debug_module, message=message, context=context)


class MatterDescriptorBase(MatterCoreBase):
    """
    Function:
        Define common behavior for descriptor versions of matter core objects.
    Args:
        None.
    Implementation Logic:
        Descriptors already are the canonical stable representation, so
        ``toDescriptor`` returns the object itself.
    """

    _debug_module: ClassVar[str] = "descriptor.core"

    def toDescriptor(self) -> "MatterDescriptorBase":
        """
        Function:
            Return the descriptor representation of the current object.
        Args:
            None.
        Returns:
            MatterDescriptorBase: Current descriptor instance.
        Implementation Logic:
            Descriptor objects are already in canonical descriptor form.
        """

        return self


class MatterLogicBase(MatterCoreBase):
    """
    Function:
        Define the abstract behavior shared by logic versions of core objects.
    Args:
        None.
    Implementation Logic:
        Logic objects act as the business entry point and own LDC conversions.
    """

    _debug_module: ClassVar[str] = "logic.core"


class MatterCalculusBase(MatterCoreBase):
    """
    Function:
        Define the abstract behavior shared by calculus versions of core objects.
    Args:
        None.
    Implementation Logic:
        Calculus objects keep optimized computation-friendly layouts while still
        converting back into descriptors for canonical comparison.
    """

    _debug_module: ClassVar[str] = "calculus.core"
