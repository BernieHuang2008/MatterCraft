"""Shared renderer-neutral models for the MatterCraft visualizer module."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import math
from typing import Any, ClassVar

from debug_module import log
from matter_core.preset import AtomPresetDatabaseLoader


VISUALIZER_MODE_TEACHING: str = "teaching"
VISUALIZER_MODE_STRUCTURAL: str = "structural"
SUPPORTED_VISUALIZER_MODE_SET: set[str] = {
    VISUALIZER_MODE_TEACHING,
    VISUALIZER_MODE_STRUCTURAL,
}


@dataclass(slots=True)
class VisualizerRequest:
    """
    Function:
        Store the shared request options understood by every visualizer.
    Args:
        bMode: Requested visualizer mode.
    Implementation Logic:
        Concrete visualizer requests inherit this base so all visualizers use
        one documented mode contract.
    """

    bMode: str = VISUALIZER_MODE_TEACHING


@dataclass(slots=True)
class VisualSceneNode:
    """
    Function:
        Represent one selectable renderer-neutral scene node.
    Args:
        The fields describe identity, label, location, hit area and metadata.
    Implementation Logic:
        Renderers consume this serialized node shape instead of reading
        matter-core objects directly.
    """

    _id: str
    bNodeType: str
    bLabel: str
    bPosition: tuple[float, float, float]
    bHitRadius: float = 18.0
    bStyle: dict[str, Any] = field(default_factory=dict)
    bPayload: dict[str, Any] = field(default_factory=dict)
    bIsInteractive: bool = True
    bIsSelected: bool = False
    bIsVisible: bool = True


@dataclass(slots=True)
class VisualSceneEdge:
    """
    Function:
        Represent one renderer-neutral relation between scene nodes.
    Args:
        The fields describe endpoints, label, style and metadata.
    Implementation Logic:
        Edges store bonds, interactions or macro relations without prescribing a
        concrete drawing backend.
    """

    _id: str
    bEdgeType: str
    bSourceNodeId: str
    bTargetNodeId: str
    bLabel: str
    bStyle: dict[str, Any] = field(default_factory=dict)
    bPayload: dict[str, Any] = field(default_factory=dict)
    bIsSelected: bool = False


@dataclass(slots=True)
class VisualCameraState:
    """
    Function:
        Store camera and viewport-independent interaction state.
    Args:
        bRotationX: Vertical orbit angle in radians.
        bRotationY: Horizontal orbit angle in radians.
        bPanX: Screen-space pan offset on x axis.
        bPanY: Screen-space pan offset on y axis.
        bZoom: Screen pixels per world unit.
    Implementation Logic:
        The camera intentionally stays simple so Tk, Pygame or Three.js layers
        can all interpret the same interaction state.
    """

    bRotationX: float = 0.0
    bRotationY: float = 0.0
    bPanX: float = 0.0
    bPanY: float = 0.0
    bZoom: float = 90.0
    bMinZoom: float = 24.0
    bMaxZoom: float = 420.0


@dataclass(slots=True)
class VisualViewport:
    """
    Function:
        Store the current renderer viewport size.
    Args:
        bWidth: Viewport width in pixels.
        bHeight: Viewport height in pixels.
    Implementation Logic:
        Interaction math needs viewport dimensions to project world nodes into
        screen coordinates for hit testing and centered zoom.
    """

    bWidth: float
    bHeight: float


@dataclass(slots=True)
class VisualInteractionState:
    """
    Function:
        Store transient pointer state between mouse events.
    Args:
        The fields capture active button, drag start and latest pointer position.
    Implementation Logic:
        Keeping transient state outside the renderer lets the visualizer define
        consistent controls across future UI backends.
    """

    bActiveButton: str | None = None
    bStartX: float = 0.0
    bStartY: float = 0.0
    bLastX: float = 0.0
    bLastY: float = 0.0
    bWasDragged: bool = False
    bSelectedNodeId: str | None = None


@dataclass(slots=True)
class VisualScene:
    """
    Function:
        Store one complete renderer-neutral visual scene.
    Args:
        bNodeList: Scene node list.
        bEdgeList: Scene edge list.
        bCameraState: Current camera state.
        bInteractionState: Current pointer interaction state.
    Implementation Logic:
        Scene, camera and interaction state travel together so UI layers can
        render and manipulate one self-contained visual payload.
    """

    bNodeList: list[VisualSceneNode]
    bEdgeList: list[VisualSceneEdge]
    bLayoutType: str
    bCameraPreset: str
    bCameraState: VisualCameraState = field(default_factory=VisualCameraState)
    bInteractionState: VisualInteractionState = field(default_factory=VisualInteractionState)
    bBackgroundStyle: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VisualPanelEntry:
    """
    Function:
        Represent one labeled information row in the side panel.
    Args:
        bLabel: User-facing label.
        bValue: User-facing value.
        bValueType: Optional rendering hint.
    Implementation Logic:
        The panel remains structured so renderers can show compact details or
        richer inspection surfaces from the same payload.
    """

    bLabel: str
    bValue: str
    bValueType: str = "text"


@dataclass(slots=True)
class VisualPanelSection:
    """
    Function:
        Represent one titled side-panel section.
    Args:
        bTitle: Section title.
        bEntryList: Structured entry rows.
        bNarrativeLineList: Short explanatory lines.
    Implementation Logic:
        Sections keep summaries, orbital boxes and selected-object details
        separate without forcing a concrete UI layout.
    """

    _id: str
    bTitle: str
    bEntryList: list[VisualPanelEntry] = field(default_factory=list)
    bNarrativeLineList: list[str] = field(default_factory=list)
    bIsCollapsed: bool = False


@dataclass(slots=True)
class VisualPanel:
    """
    Function:
        Store the side-panel payload for one visual model.
    Args:
        bTitle: Panel title.
        bSectionList: Panel section list.
        bFooterNoteList: Shared bottom notes.
    Implementation Logic:
        The panel carries teaching and structural explanations while leaving
        exact widget placement to the renderer.
    """

    bTitle: str
    bSectionList: list[VisualPanelSection]
    bFooterNoteList: list[str] = field(default_factory=list)


@dataclass(slots=True)
class VisualSelectionState:
    """
    Function:
        Store semantic selection state for one visual model.
    Args:
        The fields capture selected object and optional atom-specific drilldown.
    Implementation Logic:
        Generic selection fields are reused by all visualizers, while optional
        atom fields support subshell, orbital and electron focus.
    """

    bStateName: str
    bSelectedObjectId: str | None = None
    bSelectedSubshell: str | None = None
    bSelectedOrbitalIndex: int | None = None
    bSelectedElectronSpin: str | None = None


@dataclass(slots=True)
class VisualActionHint:
    """
    Function:
        Represent one interaction action available in the current model.
    Args:
        bActionType: Action name such as select, expand or drilldown.
        bTargetObjectId: Target object identifier.
        bLabel: Human-readable action label.
    Implementation Logic:
        Action hints let controllers and renderers expose possible operations
        without hard-coding every visualizer's internals.
    """

    _id: str
    bActionType: str
    bTargetObjectId: str
    bLabel: str
    bPayload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VisualModel:
    """
    Function:
        Store the full output of one visualizer pass.
    Args:
        The fields bind source identity, scene, panel, selection and actions.
    Implementation Logic:
        One top-level view model gives every visualizer the same output shape,
        which keeps future renderer integration predictable.
    """

    _id: str
    bSourceObjectType: str
    bSourceObjectId: str
    bMode: str
    bScene: VisualScene
    bPanel: VisualPanel
    bSelectionState: VisualSelectionState
    bActionHintList: list[VisualActionHint] = field(default_factory=list)


class VisualizerBase:
    """
    Function:
        Provide shared validation, panel and debug helpers for visualizers.
    Args:
        None.
    Implementation Logic:
        Concrete visualizers inherit this base so all four layers validate mode
        names and log through the same debug pipeline.
    """

    _debug_module: ClassVar[str] = "visualizer.base"

    def _validateMode(self, mode: str) -> str:
        """
        Function:
            Validate one requested visualizer mode.
        Args:
            mode: Mode string to validate.
        Returns:
            str: Validated mode string.
        Implementation Logic:
            The module currently documents only teaching and structural modes.
        """

        if mode not in SUPPORTED_VISUALIZER_MODE_SET:
            raise ValueError(f"Unsupported visualizer mode: {mode}")
        return mode

    def _logDebug(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        level: str = "debug",
    ) -> None:
        """
        Function:
            Emit one visualizer debug event.
        Args:
            message: Human-readable message.
            context: Optional structured context.
            level: Debug level.
        Returns:
            None.
        Implementation Logic:
            Every visualizer event is routed through the central debug module.
        """

        log(level=level, module=self._debug_module, message=message, context=context)

    @staticmethod
    def _buildPanelEntry(label: str, value: Any, valueType: str = "text") -> VisualPanelEntry:
        """
        Function:
            Build one panel entry from an arbitrary value.
        Args:
            label: Entry label.
            value: Entry value.
            valueType: Rendering hint.
        Returns:
            VisualPanelEntry: Structured panel row.
        Implementation Logic:
            The helper makes panel values deterministic when optional fields are
            currently unset.
        """

        return VisualPanelEntry(bLabel=label, bValue="None" if value is None else str(value), bValueType=valueType)

    @staticmethod
    def _buildCirclePosition(index: int, total: int, radius: float, z: float = 0.0) -> tuple[float, float, float]:
        """
        Function:
            Build one deterministic circular-layout world position.
        Args:
            index: Zero-based item index.
            total: Total item count.
            radius: Layout radius.
            z: Fixed z value.
        Returns:
            tuple[float, float, float]: World position.
        Implementation Logic:
            A deterministic first layout is enough for useful interaction and
            keeps the module dependency-free.
        """

        if total <= 1:
            return 0.0, 0.0, z
        angle = (2.0 * math.pi * index) / total
        return radius * math.cos(angle), radius * math.sin(angle), z


@lru_cache(maxsize=1)
def _loadAtomMetadataByAtomicNumber() -> dict[int, dict[str, Any]]:
    """
    Function:
        Load atom preset metadata indexed by atomic number.
    Args:
        None.
    Returns:
        dict[int, dict[str, Any]]: Metadata map.
    Implementation Logic:
        Visualizers only need friendly labels, so one cached CSV pass avoids
        repeated file reads during rendering.
    """

    loader = AtomPresetDatabaseLoader()
    return {
        record.atomicNumber: {
            "symbol": record.symbol,
            "englishName": record.englishName,
            "family": record.family,
            "block": record.block,
            "period": record.period,
        }
        for record in loader.load().values()
    }


def resolveAtomMetadata(atomicNumber: int) -> dict[str, Any]:
    """
    Function:
        Resolve friendly atom metadata for one atomic number.
    Args:
        atomicNumber: Atomic number to resolve.
    Returns:
        dict[str, Any]: Metadata dictionary.
    Implementation Logic:
        A fallback keeps the visualizer usable even if preset data is missing or
        not yet generated.
    """

    try:
        metadata = _loadAtomMetadataByAtomicNumber()
    except Exception:
        metadata = {}
    return metadata.get(
        atomicNumber,
        {
            "symbol": f"Z{atomicNumber}",
            "englishName": f"Element {atomicNumber}",
            "family": "unknown",
            "block": "unknown",
            "period": 0,
        },
    )
