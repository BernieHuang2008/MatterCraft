"""Mixture visualizer with selectable component scene nodes."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from matter_core.core_classes.mixture import MixtureLogic

from .common import (
    VISUALIZER_MODE_TEACHING,
    VisualActionHint,
    VisualModel,
    VisualPanel,
    VisualPanelSection,
    VisualScene,
    VisualSceneNode,
    VisualSelectionState,
    VisualizerBase,
    VisualizerRequest,
)


@dataclass(slots=True)
class MixtureVisualizerRequest(VisualizerRequest):
    """
    Function:
        Store mixture visualizer request state.
    Args:
        bSelectedComponentId: Selected component ID.
    Implementation Logic:
        Mixture selection is component-centric because this layer focuses on
        composition, fraction and macro distribution.
    """

    bSelectedComponentId: str | None = None


class MixtureVisualizer(VisualizerBase):
    """
    Function:
        Build mixture visual models and map clicked nodes to mixture requests.
    Args:
        None.
    Implementation Logic:
        Components become proportion-aware selectable nodes that can later drill
        into matter-level views.
    """

    _debug_module: str = "visualizer.mixture"

    def buildVisualModel(self, mixture: MixtureLogic, request: MixtureVisualizerRequest | None = None) -> VisualModel:
        """
        Function:
            Build one mixture visual model.
        Args:
            mixture: Source mixture logic object.
            request: Optional mixture request.
        Returns:
            VisualModel: Renderer-neutral mixture visual model.
        Implementation Logic:
            The scene places components in a ring and uses amount fraction as a
            sizing hint for future renderers.
        """

        active_request = request or MixtureVisualizerRequest()
        mode = self._validateMode(active_request.bMode)
        total_amount = _totalAmount(mixture)
        node_list = []
        for index, component in enumerate(mixture.bMixtureComponentList):
            fraction = Decimal("0") if total_amount == 0 else Decimal(component.bAmount) / total_amount
            node_list.append(
                VisualSceneNode(
                    _id=component._id,
                    bNodeType="component",
                    bLabel=component._id,
                    bPosition=self._buildCirclePosition(index, len(mixture.bMixtureComponentList), 2.8),
                    bHitRadius=28.0 + float(fraction) * 18.0,
                    bStyle={"shape": "component", "fraction": str(fraction)},
                    bPayload={"componentId": component._id, "drilldownVisualizer": "matter"},
                    bIsSelected=component._id == active_request.bSelectedComponentId,
                )
            )
        scene = VisualScene(node_list, [], "mixture_components", "orthographic" if mode == VISUALIZER_MODE_TEACHING else "orbit", bBackgroundStyle={"color": "#0a1013"})
        return VisualModel(
            _id=f"visual.mixture.{mixture._id}",
            bSourceObjectType="Mixture",
            bSourceObjectId=mixture._id,
            bMode=mode,
            bScene=scene,
            bPanel=self._buildPanel(mixture, active_request, mode),
            bSelectionState=self._buildSelectionState(active_request),
            bActionHintList=self._buildActionHintList(mixture),
        )

    def applySelection(self, request: MixtureVisualizerRequest, selectedNode: VisualSceneNode | None) -> MixtureVisualizerRequest:
        """
        Function:
            Convert a clicked mixture scene node into a new mixture request.
        Args:
            request: Current mixture request.
            selectedNode: Node returned by hit testing.
        Returns:
            MixtureVisualizerRequest: Updated request.
        Implementation Logic:
            Component nodes map directly to selected component request state.
        """

        if selectedNode is None:
            return MixtureVisualizerRequest(bMode=request.bMode)
        if selectedNode.bNodeType == "component":
            return MixtureVisualizerRequest(bMode=request.bMode, bSelectedComponentId=str(selectedNode.bPayload["componentId"]))
        return request

    def _buildPanel(self, mixture: MixtureLogic, request: MixtureVisualizerRequest, mode: str) -> VisualPanel:
        """
        Function:
            Build mixture side-panel data.
        Args:
            mixture: Source mixture.
            request: Current request.
            mode: Validated visualizer mode.
        Returns:
            VisualPanel: Mixture panel.
        Implementation Logic:
            The panel keeps macro composition data visible and records the
            selected component for future detailed rendering.
        """

        return VisualPanel(
            bTitle=f"Visualize Mixture: {mixture._id}",
            bSectionList=[
                VisualPanelSection(
                    _id=f"{mixture._id}.summary",
                    bTitle="Mixture Summary",
                    bEntryList=[
                        self._buildPanelEntry("Mode", mode),
                        self._buildPanelEntry("Mixture Type", mixture.bMixtureType),
                        self._buildPanelEntry("Component Count", len(mixture.bMixtureComponentList)),
                        self._buildPanelEntry("Selected Component", request.bSelectedComponentId),
                    ],
                )
            ],
        )

    def _buildSelectionState(self, request: MixtureVisualizerRequest) -> VisualSelectionState:
        """
        Function:
            Build mixture semantic selection state.
        Args:
            request: Current mixture request.
        Returns:
            VisualSelectionState: Selection state.
        Implementation Logic:
            The state is overview until a component is selected.
        """

        if request.bSelectedComponentId is not None:
            return VisualSelectionState("component_selected", request.bSelectedComponentId)
        return VisualSelectionState("overview")

    def _buildActionHintList(self, mixture: MixtureLogic) -> list[VisualActionHint]:
        """
        Function:
            Build mixture action hints.
        Args:
            mixture: Source mixture.
        Returns:
            list[VisualActionHint]: Action hints.
        Implementation Logic:
            Hints mirror the selectable component nodes.
        """

        return [
            VisualActionHint(f"{mixture._id}.select_component.{component._id}", "select_component", component._id, f"Select component {component._id}")
            for component in mixture.bMixtureComponentList
        ]


def _totalAmount(mixture: MixtureLogic) -> Decimal:
    """
    Function:
        Calculate mixture total component amount.
    Args:
        mixture: Source mixture.
    Returns:
        Decimal: Total amount.
    Implementation Logic:
        Decimal arithmetic keeps amount summaries stable for normalized strings.
    """

    return sum(Decimal(component.bAmount) for component in mixture.bMixtureComponentList)
