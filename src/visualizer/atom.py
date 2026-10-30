"""Atom visualizer with renderer-neutral selection and interaction state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matter_core.core_classes.atom import AtomLogic, SUBSHELL_ORDER

from .common import (
    VISUALIZER_MODE_STRUCTURAL,
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
    resolveAtomMetadata,
)


NOBLE_GAS_CORE_LIST: list[dict[str, Any]] = [
    {"symbol": "He", "config": {"1s": 2}},
    {"symbol": "Ne", "config": {"1s": 2, "2s": 2, "2p": 6}},
    {"symbol": "Ar", "config": {"1s": 2, "2s": 2, "2p": 6, "3s": 2, "3p": 6}},
]


@dataclass(slots=True)
class AtomVisualizerRequest(VisualizerRequest):
    """
    Function:
        Store atom-specific visualizer request state.
    Args:
        bMode: Teaching or structural mode.
        bExpandCoreDepth: Atomic-core expansion depth.
        bSelectedSubshell: Selected subshell label.
        bSelectedOrbitalIndex: Selected orbital index in the subshell.
        bSelectedElectronSpin: Selected electron spin label.
    Implementation Logic:
        The request directly mirrors the documented atom interaction ladder so a
        renderer can rebuild the view after each click.
    """

    bExpandCoreDepth: int = 0
    bSelectedSubshell: str | None = None
    bSelectedOrbitalIndex: int | None = None
    bSelectedElectronSpin: str | None = None


class AtomVisualizer(VisualizerBase):
    """
    Function:
        Build atom visual models and map clicked nodes back to atom requests.
    Args:
        None.
    Implementation Logic:
        The atom visualizer outputs a readable teaching layout first, then adds
        structural orbital-cloud nodes when the request drills deeper.
    """

    _debug_module: str = "visualizer.atom"

    def buildVisualModel(self, atom: AtomLogic, request: AtomVisualizerRequest | None = None) -> VisualModel:
        """
        Function:
            Build one atom visual model.
        Args:
            atom: Source atom logic object.
            request: Optional atom request.
        Returns:
            VisualModel: Renderer-neutral atom visual model.
        Implementation Logic:
            The build derives electron notation, scene nodes, orbital boxes and
            side-panel sections from the source atom without mutating it.
        """

        active_request = request or AtomVisualizerRequest()
        mode = self._validateMode(active_request.bMode)
        flat_config = _flattenElectronConfig(atom.bElectronConfig)
        notation_tokens = self._buildNotationTokenList(flat_config, active_request.bExpandCoreDepth)
        scene = self._buildScene(atom, active_request, notation_tokens, mode)
        panel = self._buildPanel(atom, active_request, notation_tokens, flat_config, mode)
        selection_state = self._buildSelectionState(active_request)
        model = VisualModel(
            _id=f"visual.atom.{atom._id}",
            bSourceObjectType="Atom",
            bSourceObjectId=atom._id,
            bMode=mode,
            bScene=scene,
            bPanel=panel,
            bSelectionState=selection_state,
            bActionHintList=self._buildActionHintList(atom),
        )
        self._logDebug("Atom visual model built.", {"atomId": atom._id, "mode": mode})
        return model

    def applySelection(self, request: AtomVisualizerRequest, selectedNode: VisualSceneNode | None) -> AtomVisualizerRequest:
        """
        Function:
            Convert a clicked atom scene node into a new atom request.
        Args:
            request: Current atom request.
            selectedNode: Node returned by interaction hit testing.
        Returns:
            AtomVisualizerRequest: Updated request.
        Implementation Logic:
            Node payload types define the documented click behavior: core
            expands, subshell opens boxes, orbital opens cloud and electron
            stores spin focus.
        """

        if selectedNode is None:
            return AtomVisualizerRequest(bMode=request.bMode)
        node_type = selectedNode.bNodeType
        payload = selectedNode.bPayload
        if node_type == "atomic_core":
            return AtomVisualizerRequest(bMode=request.bMode, bExpandCoreDepth=request.bExpandCoreDepth + 1)
        if node_type == "subshell":
            return AtomVisualizerRequest(
                bMode=request.bMode,
                bExpandCoreDepth=request.bExpandCoreDepth,
                bSelectedSubshell=str(payload["subshell"]),
            )
        if node_type == "orbital_box":
            return AtomVisualizerRequest(
                bMode=request.bMode,
                bExpandCoreDepth=request.bExpandCoreDepth,
                bSelectedSubshell=str(payload["subshell"]),
                bSelectedOrbitalIndex=int(payload["orbitalIndex"]),
            )
        if node_type == "electron_arrow":
            return AtomVisualizerRequest(
                bMode=request.bMode,
                bExpandCoreDepth=request.bExpandCoreDepth,
                bSelectedSubshell=str(payload["subshell"]),
                bSelectedOrbitalIndex=int(payload["orbitalIndex"]),
                bSelectedElectronSpin=str(payload["spin"]),
            )
        return request

    def _buildScene(
        self,
        atom: AtomLogic,
        request: AtomVisualizerRequest,
        notationTokenList: list[dict[str, Any]],
        mode: str,
    ) -> VisualScene:
        """
        Function:
            Build atom scene nodes and edges.
        Args:
            atom: Source atom.
            request: Current request.
            notationTokenList: Visible notation tokens.
            mode: Validated visualizer mode.
        Returns:
            VisualScene: Atom visual scene.
        Implementation Logic:
            Nodes are positioned in a mostly 2D layout, with orbital boxes and
            electron arrows represented as selectable scene nodes.
        """

        metadata = resolveAtomMetadata(atom.bAtomicNumber)
        node_list = [
            VisualSceneNode(
                _id=f"{atom._id}.nucleus",
                bNodeType="nucleus",
                bLabel=f"+{atom.bAtomicNumber}",
                bPosition=(0.0, 0.0, 0.0),
                bHitRadius=34.0,
                bStyle={"color": "#ff9e59", "shape": "glow_sphere"},
                bPayload={"symbol": metadata["symbol"], "atomicNumber": atom.bAtomicNumber},
            )
        ]

        for index, token in enumerate(notationTokenList):
            node_list.append(
                VisualSceneNode(
                    _id=f"{atom._id}.notation.{index}",
                    bNodeType=token["nodeType"],
                    bLabel=token["label"],
                    bPosition=(-1.8 + index * 1.2, 1.35, 0.0),
                    bHitRadius=26.0,
                    bStyle={"color": token["color"]},
                    bPayload=token["payload"],
                    bIsSelected=token["payload"].get("subshell") == request.bSelectedSubshell,
                )
            )

        if request.bSelectedSubshell in atom.bElectronConfig:
            occupancy = atom.bElectronConfig[request.bSelectedSubshell]
            for orbital_index, electron_count in enumerate(occupancy):
                x_position = -0.9 + orbital_index * 0.9
                is_selected = orbital_index == request.bSelectedOrbitalIndex
                node_list.append(
                    VisualSceneNode(
                        _id=f"{atom._id}.orbital.{request.bSelectedSubshell}.{orbital_index}",
                        bNodeType="orbital_box",
                        bLabel=f"[{orbital_index}]",
                        bPosition=(x_position, -1.15, 0.0),
                        bHitRadius=24.0,
                        bStyle={"shape": "box", "color": "#d8e2f2"},
                        bPayload={"subshell": request.bSelectedSubshell, "orbitalIndex": orbital_index},
                        bIsSelected=is_selected,
                    )
                )
                if electron_count >= 1:
                    node_list.append(self._buildElectronNode(atom._id, request.bSelectedSubshell, orbital_index, "up", x_position, -0.86))
                if electron_count >= 2:
                    node_list.append(self._buildElectronNode(atom._id, request.bSelectedSubshell, orbital_index, "down", x_position, -1.44))

        if request.bSelectedSubshell is not None and request.bSelectedOrbitalIndex is not None:
            node_list.append(
                VisualSceneNode(
                    _id=f"{atom._id}.cloud",
                    bNodeType="orbital_cloud",
                    bLabel=_buildCloudLabel(request.bSelectedSubshell, request.bSelectedOrbitalIndex),
                    bPosition=(1.7, -1.0, 0.35 if mode == VISUALIZER_MODE_STRUCTURAL else 0.0),
                    bHitRadius=32.0,
                    bStyle={"shape": _cloudShape(request.bSelectedSubshell), "color": "#8ac6ff"},
                    bPayload={"subshell": request.bSelectedSubshell, "orbitalIndex": request.bSelectedOrbitalIndex},
                    bIsInteractive=False,
                    bIsSelected=True,
                )
            )

        return VisualScene(
            bNodeList=node_list,
            bEdgeList=[],
            bLayoutType="atom_teaching_focus",
            bCameraPreset="orthographic" if mode == VISUALIZER_MODE_TEACHING else "orbit",
            bBackgroundStyle={"color": "#05070b"},
        )

    def _buildElectronNode(
        self,
        atomId: str,
        subshell: str,
        orbitalIndex: int,
        spin: str,
        x: float,
        y: float,
    ) -> VisualSceneNode:
        """
        Function:
            Build one selectable electron-arrow node.
        Args:
            atomId: Source atom ID.
            subshell: Subshell label.
            orbitalIndex: Orbital index.
            spin: Spin label.
            x: World x position.
            y: World y position.
        Returns:
            VisualSceneNode: Electron-arrow node.
        Implementation Logic:
            Electron arrows are real hit-test targets so clicking an arrow can
            enter the documented electron-selected state.
        """

        return VisualSceneNode(
            _id=f"{atomId}.electron.{subshell}.{orbitalIndex}.{spin}",
            bNodeType="electron_arrow",
            bLabel=spin,
            bPosition=(x, y, 0.0),
            bHitRadius=16.0,
            bStyle={"shape": "arrow", "color": "#f7d36b"},
            bPayload={"subshell": subshell, "orbitalIndex": orbitalIndex, "spin": spin},
        )

    def _buildPanel(
        self,
        atom: AtomLogic,
        request: AtomVisualizerRequest,
        notationTokenList: list[dict[str, Any]],
        flatConfig: dict[str, int],
        mode: str,
    ) -> VisualPanel:
        """
        Function:
            Build atom side-panel data.
        Args:
            atom: Source atom.
            request: Current atom request.
            notationTokenList: Visible notation tokens.
            flatConfig: Flattened electron config.
            mode: Validated visualizer mode.
        Returns:
            VisualPanel: Atom panel.
        Implementation Logic:
            The panel mirrors the scene selection state and keeps the theory
            warning visible in a renderer-neutral form.
        """

        metadata = resolveAtomMetadata(atom.bAtomicNumber)
        section_list = [
            VisualPanelSection(
                _id=f"{atom._id}.summary",
                bTitle="Atom Summary",
                bEntryList=[
                    self._buildPanelEntry("Symbol", metadata["symbol"]),
                    self._buildPanelEntry("Atomic Number", atom.bAtomicNumber),
                    self._buildPanelEntry("Mass Number", atom.bMassNumber),
                    self._buildPanelEntry("Charge", atom.bCharge),
                    self._buildPanelEntry("Electron Count", atom.aElectronCount),
                    self._buildPanelEntry("Valence Electron Count", atom.aValenceElectronCount),
                ],
            ),
            VisualPanelSection(
                _id=f"{atom._id}.notation",
                bTitle="Electron Notation",
                bEntryList=[
                    self._buildPanelEntry("Mode", mode),
                    self._buildPanelEntry("Visible Notation", " ".join(token["label"] for token in notationTokenList), "code"),
                    self._buildPanelEntry("Full Notation", _buildNotationText(flatConfig), "code"),
                    self._buildPanelEntry("Selected Subshell", request.bSelectedSubshell),
                    self._buildPanelEntry("Selected Orbital", request.bSelectedOrbitalIndex),
                    self._buildPanelEntry("Selected Spin", request.bSelectedElectronSpin),
                ],
                bNarrativeLineList=[
                    "This is a teaching-friendly quantum approximation, not a classical electron orbit recording.",
                    "Structural mode is reserved for richer probability-density and wavefunction data later.",
                ],
            ),
        ]
        if request.bSelectedSubshell in atom.bElectronConfig:
            section_list.append(
                VisualPanelSection(
                    _id=f"{atom._id}.orbital_box",
                    bTitle=f"Orbital Box: {request.bSelectedSubshell}",
                    bEntryList=[
                        self._buildPanelEntry("Box View", _buildBoxText(atom.bElectronConfig[request.bSelectedSubshell]), "code"),
                    ],
                )
            )
        return VisualPanel(bTitle=f"Visualize Atom: {metadata['symbol']}", bSectionList=section_list)

    def _buildSelectionState(self, request: AtomVisualizerRequest) -> VisualSelectionState:
        """
        Function:
            Build atom semantic selection state.
        Args:
            request: Current atom request.
        Returns:
            VisualSelectionState: Selection state.
        Implementation Logic:
            The state follows the documented atom interaction ladder.
        """

        if request.bSelectedElectronSpin is not None:
            state_name = "electron_selected"
        elif request.bSelectedOrbitalIndex is not None:
            state_name = "orbital_selected"
        elif request.bSelectedSubshell is not None:
            state_name = "subshell_selected"
        elif request.bExpandCoreDepth > 0:
            state_name = "core_expanded"
        else:
            state_name = "overview"
        return VisualSelectionState(
            bStateName=state_name,
            bSelectedSubshell=request.bSelectedSubshell,
            bSelectedOrbitalIndex=request.bSelectedOrbitalIndex,
            bSelectedElectronSpin=request.bSelectedElectronSpin,
        )

    def _buildActionHintList(self, atom: AtomLogic) -> list[VisualActionHint]:
        """
        Function:
            Build atom action hints.
        Args:
            atom: Source atom.
        Returns:
            list[VisualActionHint]: Available atom actions.
        Implementation Logic:
            The first hints expose selectable subshells so renderers can present
            controls in addition to pointer hit testing.
        """

        return [
            VisualActionHint(
                _id=f"{atom._id}.action.select.{label}",
                bActionType="select_subshell",
                bTargetObjectId=label,
                bLabel=f"Select {label}",
                bPayload={"subshell": label},
            )
            for label in _sortOrbitalLabels(list(atom.bElectronConfig.keys()))
        ]

    def _buildNotationTokenList(self, flatConfig: dict[str, int], expandDepth: int) -> list[dict[str, Any]]:
        """
        Function:
            Build visible electron-notation scene tokens.
        Args:
            flatConfig: Flattened electron config.
            expandDepth: Atomic-core expansion depth.
        Returns:
            list[dict[str, Any]]: Notation token list.
        Implementation Logic:
            The first implementation uses a noble-gas core when one matches and
            exposes that core as a selectable expansion target.
        """

        core = _findBestCore(flatConfig)
        if core is None or expandDepth > 0:
            return _buildOrbitalTokens(flatConfig)
        outer_config = _subtractConfig(flatConfig, core["config"])
        return [
            {
                "label": f"[{core['symbol']}]",
                "nodeType": "atomic_core",
                "color": "#8ac6ff",
                "payload": {"coreSymbol": core["symbol"]},
            }
        ] + _buildOrbitalTokens(outer_config)


def _flattenElectronConfig(config: dict[str, list[int]]) -> dict[str, int]:
    """
    Function:
        Flatten occupancy lists into electron counts.
    Args:
        config: Orbital occupancy map.
    Returns:
        dict[str, int]: Electron counts by subshell.
    Implementation Logic:
        Notation logic works on total electron counts, while orbital boxes still
        use the original occupancy lists.
    """

    return {label: sum(values) for label, values in config.items() if sum(values) > 0}


def _findBestCore(flatConfig: dict[str, int]) -> dict[str, Any] | None:
    """
    Function:
        Find the largest matching noble-gas core.
    Args:
        flatConfig: Flattened electron config.
    Returns:
        dict[str, Any] | None: Core metadata.
    Implementation Logic:
        Cores are tested from largest to smallest and must match all inner
        orbital counts exactly.
    """

    for core in reversed(NOBLE_GAS_CORE_LIST):
        if all(flatConfig.get(label, 0) == count for label, count in core["config"].items()):
            return core
    return None


def _subtractConfig(config: dict[str, int], coreConfig: dict[str, int]) -> dict[str, int]:
    """
    Function:
        Remove core electrons from a flattened config.
    Args:
        config: Source config.
        coreConfig: Core config to remove.
    Returns:
        dict[str, int]: Outer config.
    Implementation Logic:
        Positive remainders become the visible valence notation after a core.
    """

    return {
        label: config.get(label, 0) - coreConfig.get(label, 0)
        for label in _sortOrbitalLabels(list(config.keys()))
        if config.get(label, 0) - coreConfig.get(label, 0) > 0
    }


def _buildOrbitalTokens(flatConfig: dict[str, int]) -> list[dict[str, Any]]:
    """
    Function:
        Build notation tokens for occupied subshells.
    Args:
        flatConfig: Flattened electron config.
    Returns:
        list[dict[str, Any]]: Subshell token list.
    Implementation Logic:
        Each subshell token is interactive and maps directly to subshell
        selection when clicked.
    """

    return [
        {
            "label": f"{label}^{flatConfig[label]}",
            "nodeType": "subshell",
            "color": "#e8eefc",
            "payload": {"subshell": label},
        }
        for label in _sortOrbitalLabels(list(flatConfig.keys()))
    ]


def _sortOrbitalLabels(labels: list[str]) -> list[str]:
    """
    Function:
        Sort orbital labels in Aufbau-style order.
    Args:
        labels: Orbital labels.
    Returns:
        list[str]: Sorted labels.
    Implementation Logic:
        The sort key uses n + l, then n, then subshell order.
    """

    return sorted(labels, key=lambda label: (int(label[:-1]) + SUBSHELL_ORDER[label[-1]], int(label[:-1]), SUBSHELL_ORDER[label[-1]]))


def _buildNotationText(flatConfig: dict[str, int]) -> str:
    """
    Function:
        Build full electron-notation text.
    Args:
        flatConfig: Flattened electron config.
    Returns:
        str: Notation text.
    Implementation Logic:
        ASCII notation keeps source output stable while UI layers can later
        render superscripts.
    """

    return " ".join(f"{label}^{flatConfig[label]}" for label in _sortOrbitalLabels(list(flatConfig.keys())))


def _buildBoxText(occupancy: list[int]) -> str:
    """
    Function:
        Build ASCII orbital box text.
    Args:
        occupancy: Orbital occupancy list.
    Returns:
        str: Box text.
    Implementation Logic:
        Each occupancy slot becomes an explicit box with up/down spin markers.
    """

    box_list = []
    for count in occupancy:
        if count <= 0:
            box_list.append("[ ]")
        elif count == 1:
            box_list.append("[up]")
        else:
            box_list.append("[up down]")
    return " ".join(box_list)


def _cloudShape(subshell: str) -> str:
    """
    Function:
        Resolve cloud shape by subshell family.
    Args:
        subshell: Subshell label.
    Returns:
        str: Cloud shape label.
    Implementation Logic:
        The shape remains a teaching approximation for the first renderer.
    """

    return {"s": "sphere", "p": "dumbbell", "d": "clover", "f": "multi_lobed"}.get(subshell[-1], "unknown")


def _buildCloudLabel(subshell: str, orbitalIndex: int) -> str:
    """
    Function:
        Build orbital cloud label text.
    Args:
        subshell: Selected subshell.
        orbitalIndex: Selected orbital index.
    Returns:
        str: Cloud label.
    Implementation Logic:
        The label connects the cloud node back to the clicked orbital box.
    """

    return f"{subshell} cloud {orbitalIndex}"
