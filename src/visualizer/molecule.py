"""Molecule visualizer with selectable atom and bond scene nodes."""

from __future__ import annotations

from dataclasses import dataclass

from matter_core.core_classes.molecule import MoleculeLogic

from .common import (
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
    resolveAtomMetadata,
)


@dataclass(slots=True)
class MoleculeVisualizerRequest(VisualizerRequest):
    """
    Function:
        Store molecule visualizer request state.
    Args:
        bSelectedAtomId: Selected atom ID.
        bSelectedBondId: Selected bond ID.
    Implementation Logic:
        Molecule selection distinguishes atom nodes from bond midpoint nodes so
        click handling can update focused panel details.
    """

    bSelectedAtomId: str | None = None
    bSelectedBondId: str | None = None


class MoleculeVisualizer(VisualizerBase):
    """
    Function:
        Build molecule visual models and map clicked nodes to molecule requests.
    Args:
        None.
    Implementation Logic:
        Atoms are scene nodes, bonds are scene edges plus midpoint hit nodes, so
        both object types can be selected by the shared controller.
    """

    _debug_module: str = "visualizer.molecule"

    def buildVisualModel(self, molecule: MoleculeLogic, request: MoleculeVisualizerRequest | None = None) -> VisualModel:
        """
        Function:
            Build one molecule visual model.
        Args:
            molecule: Source molecule logic object.
            request: Optional molecule request.
        Returns:
            VisualModel: Renderer-neutral molecule visual model.
        Implementation Logic:
            The scene uses a deterministic circular layout and exposes every
            bond through both an edge and a selectable midpoint node.
        """

        active_request = request or MoleculeVisualizerRequest()
        mode = self._validateMode(active_request.bMode)
        node_list: list[VisualSceneNode] = []
        edge_list: list[VisualSceneEdge] = []
        atom_position_map: dict[str, tuple[float, float, float]] = {}
        atom_list = list(molecule.bAtomList.values())

        for index, atom in enumerate(atom_list):
            metadata = resolveAtomMetadata(atom.bAtomicNumber)
            position = self._buildCirclePosition(index, len(atom_list), 2.2, 0.0 if mode == VISUALIZER_MODE_TEACHING else float(index % 2) * 0.35)
            atom_position_map[atom._id] = position
            node_list.append(
                VisualSceneNode(
                    _id=atom._id,
                    bNodeType="atom",
                    bLabel=metadata["symbol"],
                    bPosition=position,
                    bHitRadius=28.0,
                    bStyle={"shape": "atom", "family": metadata["family"]},
                    bPayload={"atomId": atom._id, "drilldownVisualizer": "atom"},
                    bIsSelected=atom._id == active_request.bSelectedAtomId,
                )
            )

        for bond in molecule.bBondList.values():
            source_id = bond.bAtomList[0]._id
            target_id = bond.bAtomList[1]._id
            edge_list.append(
                VisualSceneEdge(
                    _id=bond._id,
                    bEdgeType="bond",
                    bSourceNodeId=source_id,
                    bTargetNodeId=target_id,
                    bLabel=bond.bBondType,
                    bPayload={"bondId": bond._id, "bondOrder": bond.bBondOrder},
                    bIsSelected=bond._id == active_request.bSelectedBondId,
                )
            )
            if source_id in atom_position_map and target_id in atom_position_map:
                source_position = atom_position_map[source_id]
                target_position = atom_position_map[target_id]
                node_list.append(
                    VisualSceneNode(
                        _id=f"{bond._id}.hit",
                        bNodeType="bond",
                        bLabel=bond.bBondType,
                        bPosition=_midpoint(source_position, target_position),
                        bHitRadius=18.0,
                        bStyle={"shape": "bond_hit"},
                        bPayload={"bondId": bond._id},
                        bIsSelected=bond._id == active_request.bSelectedBondId,
                    )
                )

        scene = VisualScene(
            bNodeList=node_list,
            bEdgeList=edge_list,
            bLayoutType="molecule_graph",
            bCameraPreset="orthographic" if mode == VISUALIZER_MODE_TEACHING else "orbit",
            bBackgroundStyle={"color": "#0b1018"},
        )
        model = VisualModel(
            _id=f"visual.molecule.{molecule._id}",
            bSourceObjectType="Molecule",
            bSourceObjectId=molecule._id,
            bMode=mode,
            bScene=scene,
            bPanel=self._buildPanel(molecule, active_request, mode),
            bSelectionState=self._buildSelectionState(active_request),
            bActionHintList=self._buildActionHintList(molecule),
        )
        self._logDebug("Molecule visual model built.", {"moleculeId": molecule._id, "mode": mode})
        return model

    def applySelection(self, request: MoleculeVisualizerRequest, selectedNode: VisualSceneNode | None) -> MoleculeVisualizerRequest:
        """
        Function:
            Convert a clicked molecule scene node into a new molecule request.
        Args:
            request: Current molecule request.
            selectedNode: Node returned by hit testing.
        Returns:
            MoleculeVisualizerRequest: Updated request.
        Implementation Logic:
            Atom nodes select atoms and bond midpoint nodes select bonds.
        """

        if selectedNode is None:
            return MoleculeVisualizerRequest(bMode=request.bMode)
        if selectedNode.bNodeType == "atom":
            return MoleculeVisualizerRequest(bMode=request.bMode, bSelectedAtomId=str(selectedNode.bPayload["atomId"]))
        if selectedNode.bNodeType == "bond":
            return MoleculeVisualizerRequest(bMode=request.bMode, bSelectedBondId=str(selectedNode.bPayload["bondId"]))
        return request

    def _buildPanel(self, molecule: MoleculeLogic, request: MoleculeVisualizerRequest, mode: str) -> VisualPanel:
        """
        Function:
            Build molecule side-panel data.
        Args:
            molecule: Source molecule.
            request: Current request.
            mode: Validated visualizer mode.
        Returns:
            VisualPanel: Molecule panel.
        Implementation Logic:
            Summary and selected-object details are separated so renderers can
            keep the molecule view compact.
        """

        section_list = [
            VisualPanelSection(
                _id=f"{molecule._id}.summary",
                bTitle="Molecule Summary",
                bEntryList=[
                    self._buildPanelEntry("Mode", mode),
                    self._buildPanelEntry("Atom Count", len(molecule.bAtomList)),
                    self._buildPanelEntry("Bond Count", len(molecule.bBondList)),
                    self._buildPanelEntry("Selected Atom", request.bSelectedAtomId),
                    self._buildPanelEntry("Selected Bond", request.bSelectedBondId),
                ],
            )
        ]
        if request.bSelectedAtomId in molecule.bAtomList:
            atom = molecule.bAtomList[request.bSelectedAtomId]
            metadata = resolveAtomMetadata(atom.bAtomicNumber)
            section_list.append(
                VisualPanelSection(
                    _id=f"{molecule._id}.selected_atom",
                    bTitle="Selected Atom",
                    bEntryList=[
                        self._buildPanelEntry("Symbol", metadata["symbol"]),
                        self._buildPanelEntry("Charge", atom.bCharge),
                        self._buildPanelEntry("Valence Electrons", atom.aValenceElectronCount),
                    ],
                )
            )
        if request.bSelectedBondId in molecule.bBondList:
            bond = molecule.bBondList[request.bSelectedBondId]
            section_list.append(
                VisualPanelSection(
                    _id=f"{molecule._id}.selected_bond",
                    bTitle="Selected Bond",
                    bEntryList=[
                        self._buildPanelEntry("Bond Type", bond.bBondType),
                        self._buildPanelEntry("Bond Order", bond.bBondOrder),
                        self._buildPanelEntry("Bond Length", bond.bBondLength),
                        self._buildPanelEntry("Bond Polarity", bond.bPolarity),
                    ],
                )
            )
        return VisualPanel(bTitle=f"Visualize Molecule: {molecule._id}", bSectionList=section_list)

    def _buildSelectionState(self, request: MoleculeVisualizerRequest) -> VisualSelectionState:
        """
        Function:
            Build molecule semantic selection state.
        Args:
            request: Current molecule request.
        Returns:
            VisualSelectionState: Selection state.
        Implementation Logic:
            Bond focus takes priority because it is the more specific local
            structure when both request fields are populated.
        """

        if request.bSelectedBondId is not None:
            return VisualSelectionState(bStateName="bond_selected", bSelectedObjectId=request.bSelectedBondId)
        if request.bSelectedAtomId is not None:
            return VisualSelectionState(bStateName="atom_selected", bSelectedObjectId=request.bSelectedAtomId)
        return VisualSelectionState(bStateName="overview")

    def _buildActionHintList(self, molecule: MoleculeLogic) -> list[VisualActionHint]:
        """
        Function:
            Build molecule action hints.
        Args:
            molecule: Source molecule.
        Returns:
            list[VisualActionHint]: Action hints.
        Implementation Logic:
            Action hints mirror the selectable atom and bond scene nodes.
        """

        hint_list = [
            VisualActionHint(f"{molecule._id}.select_atom.{atom_id}", "select_atom", atom_id, f"Select atom {atom_id}")
            for atom_id in molecule.bAtomList
        ]
        hint_list.extend(
            VisualActionHint(f"{molecule._id}.select_bond.{bond_id}", "select_bond", bond_id, f"Select bond {bond_id}")
            for bond_id in molecule.bBondList
        )
        return hint_list


def _midpoint(
    sourcePosition: tuple[float, float, float],
    targetPosition: tuple[float, float, float],
) -> tuple[float, float, float]:
    """
    Function:
        Build midpoint between two world positions.
    Args:
        sourcePosition: Source world position.
        targetPosition: Target world position.
    Returns:
        tuple[float, float, float]: Midpoint position.
    Implementation Logic:
        Bond hit nodes live at midpoint so clicking a bond feels natural in the
        first 2D/weak-3D layout.
    """

    return (
        (sourcePosition[0] + targetPosition[0]) / 2.0,
        (sourcePosition[1] + targetPosition[1]) / 2.0,
        (sourcePosition[2] + targetPosition[2]) / 2.0,
    )
