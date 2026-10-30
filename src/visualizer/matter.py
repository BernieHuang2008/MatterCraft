"""Matter visualizer with selectable molecule and interaction nodes."""

from __future__ import annotations

from dataclasses import dataclass

from matter_core.core_classes.matter import MatterLogic

from .common import (
    VISUALIZER_MODE_STRUCTURAL,
    VISUALIZER_MODE_TEACHING,
    VisualActionHint,
    VisualModel,
    VisualPanel,
    VisualPanelSection,
    VisualScene,
    VisualSceneEdge,
    VisualSceneNode,
    VisualSelectionState,
    VisualizerBase,
    VisualizerRequest,
)


@dataclass(slots=True)
class MatterVisualizerRequest(VisualizerRequest):
    """
    Function:
        Store matter visualizer request state.
    Args:
        bSelectedMoleculeId: Selected molecule ID.
        bSelectedInteractionId: Selected interaction ID.
    Implementation Logic:
        Matter selection focuses either molecule organization or a matter-level
        intermolecular interaction.
    """

    bSelectedMoleculeId: str | None = None
    bSelectedInteractionId: str | None = None


class MatterVisualizer(VisualizerBase):
    """
    Function:
        Build matter visual models and map clicked nodes to matter requests.
    Args:
        None.
    Implementation Logic:
        Molecules become selectable units and structural mode also exposes
        interaction nodes for local organization details.
    """

    _debug_module: str = "visualizer.matter"

    def buildVisualModel(self, matter: MatterLogic, request: MatterVisualizerRequest | None = None) -> VisualModel:
        """
        Function:
            Build one matter visual model.
        Args:
            matter: Source matter logic object.
            request: Optional matter request.
        Returns:
            VisualModel: Renderer-neutral matter visual model.
        Implementation Logic:
            The scene starts as a molecule cluster and adds interaction anchors
            when structural details are requested.
        """

        active_request = request or MatterVisualizerRequest()
        mode = self._validateMode(active_request.bMode)
        node_list: list[VisualSceneNode] = []
        edge_list: list[VisualSceneEdge] = []
        molecule_list = list(matter.bChemMoleculeList.values())
        for index, molecule in enumerate(molecule_list):
            node_list.append(
                VisualSceneNode(
                    _id=molecule._id,
                    bNodeType="molecule",
                    bLabel=molecule._id,
                    bPosition=self._buildCirclePosition(index, len(molecule_list), 2.8),
                    bHitRadius=32.0,
                    bStyle={"shape": "molecule_group"},
                    bPayload={"moleculeId": molecule._id, "drilldownVisualizer": "molecule"},
                    bIsSelected=molecule._id == active_request.bSelectedMoleculeId,
                )
            )
        if mode == VISUALIZER_MODE_STRUCTURAL:
            for index, interaction in enumerate(matter.bMatterIntmolInteractionList or []):
                node_list.append(
                    VisualSceneNode(
                        _id=interaction._id,
                        bNodeType="interaction",
                        bLabel=interaction.bInteractionType,
                        bPosition=(0.0, -2.4 - index * 0.7, 0.2),
                        bHitRadius=24.0,
                        bStyle={"shape": "interaction"},
                        bPayload={"interactionId": interaction._id},
                        bIsSelected=interaction._id == active_request.bSelectedInteractionId,
                    )
                )
                if molecule_list:
                    edge_list.append(VisualSceneEdge(f"{interaction._id}.anchor", "interaction", molecule_list[0]._id, interaction._id, interaction.bInteractionType))
        scene = VisualScene(node_list, edge_list, "matter_cluster", "orthographic" if mode == VISUALIZER_MODE_TEACHING else "orbit", bBackgroundStyle={"color": "#0a0f14"})
        return VisualModel(
            _id=f"visual.matter.{matter._id}",
            bSourceObjectType="Matter",
            bSourceObjectId=matter._id,
            bMode=mode,
            bScene=scene,
            bPanel=self._buildPanel(matter, active_request, mode),
            bSelectionState=self._buildSelectionState(active_request),
            bActionHintList=self._buildActionHintList(matter),
        )

    def applySelection(self, request: MatterVisualizerRequest, selectedNode: VisualSceneNode | None) -> MatterVisualizerRequest:
        """
        Function:
            Convert a clicked matter scene node into a new matter request.
        Args:
            request: Current matter request.
            selectedNode: Node returned by hit testing.
        Returns:
            MatterVisualizerRequest: Updated request.
        Implementation Logic:
            Molecule and interaction nodes map to their corresponding selected
            request fields.
        """

        if selectedNode is None:
            return MatterVisualizerRequest(bMode=request.bMode)
        if selectedNode.bNodeType == "molecule":
            return MatterVisualizerRequest(bMode=request.bMode, bSelectedMoleculeId=str(selectedNode.bPayload["moleculeId"]))
        if selectedNode.bNodeType == "interaction":
            return MatterVisualizerRequest(bMode=request.bMode, bSelectedInteractionId=str(selectedNode.bPayload["interactionId"]))
        return request

    def _buildPanel(self, matter: MatterLogic, request: MatterVisualizerRequest, mode: str) -> VisualPanel:
        """
        Function:
            Build matter side-panel data.
        Args:
            matter: Source matter.
            request: Current request.
            mode: Validated visualizer mode.
        Returns:
            VisualPanel: Matter panel.
        Implementation Logic:
            Matter panels summarize molecule organization, arrangement and the
            currently selected molecule or interaction.
        """

        return VisualPanel(
            bTitle=f"Visualize Matter: {matter._id}",
            bSectionList=[
                VisualPanelSection(
                    _id=f"{matter._id}.summary",
                    bTitle="Matter Summary",
                    bEntryList=[
                        self._buildPanelEntry("Mode", mode),
                        self._buildPanelEntry("Molecule Count", len(matter.bChemMoleculeList)),
                        self._buildPanelEntry("Molecule Gap", matter.bPhyMoleculeGap),
                        self._buildPanelEntry("Arrangement", matter.bPhyMoleculeArrangement),
                        self._buildPanelEntry("Interaction Count", len(matter.bMatterIntmolInteractionList or [])),
                        self._buildPanelEntry("Selected Molecule", request.bSelectedMoleculeId),
                        self._buildPanelEntry("Selected Interaction", request.bSelectedInteractionId),
                    ],
                )
            ],
        )

    def _buildSelectionState(self, request: MatterVisualizerRequest) -> VisualSelectionState:
        """
        Function:
            Build matter semantic selection state.
        Args:
            request: Current matter request.
        Returns:
            VisualSelectionState: Selection state.
        Implementation Logic:
            Interaction selection takes priority over molecule selection.
        """

        if request.bSelectedInteractionId is not None:
            return VisualSelectionState("interaction_selected", request.bSelectedInteractionId)
        if request.bSelectedMoleculeId is not None:
            return VisualSelectionState("molecule_selected", request.bSelectedMoleculeId)
        return VisualSelectionState("overview")

    def _buildActionHintList(self, matter: MatterLogic) -> list[VisualActionHint]:
        """
        Function:
            Build matter action hints.
        Args:
            matter: Source matter.
        Returns:
            list[VisualActionHint]: Action hints.
        Implementation Logic:
            Hints expose molecule selection and drilldown targets.
        """

        return [
            VisualActionHint(f"{matter._id}.select_molecule.{molecule_id}", "select_molecule", molecule_id, f"Select molecule {molecule_id}")
            for molecule_id in matter.bChemMoleculeList
        ]
