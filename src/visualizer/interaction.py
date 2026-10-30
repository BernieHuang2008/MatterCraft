"""Pointer and camera interaction logic for renderer-neutral visual models."""

from __future__ import annotations

from dataclasses import dataclass
import math

from debug_module import log

from .common import VisualCameraState, VisualModel, VisualSceneNode, VisualViewport


@dataclass(slots=True)
class VisualPointerEvent:
    """
    Function:
        Store one normalized pointer or wheel event from a renderer.
    Args:
        bX: Pointer x coordinate in pixels.
        bY: Pointer y coordinate in pixels.
        bButton: Button name such as left, middle or right.
        bWheelDelta: Wheel delta, positive means zoom in.
    Implementation Logic:
        UI-specific events are normalized into this small shape before reaching
        the visualizer interaction controller.
    """

    bX: float
    bY: float
    bButton: str | None = None
    bWheelDelta: float = 0.0


@dataclass(slots=True)
class VisualInteractionResult:
    """
    Function:
        Store the result of one interaction-controller update.
    Args:
        bDidChangeCamera: Whether camera state changed.
        bSelectedNodeId: Node selected by a click, if any.
        bSelectedNode: Selected scene node, if any.
        bInteractionName: Interaction operation name.
    Implementation Logic:
        Returning structured results lets callers decide whether to rebuild the
        visual model, update only the camera, or apply a selection.
    """

    bDidChangeCamera: bool = False
    bSelectedNodeId: str | None = None
    bSelectedNode: VisualSceneNode | None = None
    bInteractionName: str = "none"


class VisualInteractionController:
    """
    Function:
        Apply camera and selection interactions to renderer-neutral visual models.
    Args:
        bDragThreshold: Pixel movement before a click becomes a drag.
        bRotateSensitivity: Radians per dragged pixel for left-button rotation.
        bPanSensitivity: Pixels of pan per dragged pixel for middle-button pan.
        bZoomStep: Multiplicative zoom step for one wheel unit.
    Implementation Logic:
        The controller implements the expected viewport gestures: middle-drag
        pans, wheel zooms around the mouse, left-drag rotates and left-click
        selects the closest hit node.
    """

    def __init__(
        self,
        bDragThreshold: float = 4.0,
        bRotateSensitivity: float = 0.01,
        bPanSensitivity: float = 1.0,
        bZoomStep: float = 1.12,
    ) -> None:
        """
        Function:
            Initialize the shared interaction controller.
        Args:
            bDragThreshold: Pixel threshold separating click from drag.
            bRotateSensitivity: Rotation sensitivity.
            bPanSensitivity: Pan sensitivity.
            bZoomStep: Per-wheel zoom multiplier.
        Returns:
            None.
        Implementation Logic:
            Sensitivities are constructor options so renderers can tune feel
            without rewriting interaction behavior.
        """

        self.bDragThreshold = bDragThreshold
        self.bRotateSensitivity = bRotateSensitivity
        self.bPanSensitivity = bPanSensitivity
        self.bZoomStep = bZoomStep

    def handlePointerDown(self, model: VisualModel, event: VisualPointerEvent) -> VisualInteractionResult:
        """
        Function:
            Start a pointer interaction.
        Args:
            model: Current visual model.
            event: Pointer-down event.
        Returns:
            VisualInteractionResult: Interaction result.
        Implementation Logic:
            The controller records the starting pointer position and active
            button so future move/up events can decide click versus drag.
        """

        state = model.bScene.bInteractionState
        state.bActiveButton = event.bButton
        state.bStartX = event.bX
        state.bStartY = event.bY
        state.bLastX = event.bX
        state.bLastY = event.bY
        state.bWasDragged = False
        return VisualInteractionResult(bInteractionName="pointer_down")

    def handlePointerMove(self, model: VisualModel, event: VisualPointerEvent) -> VisualInteractionResult:
        """
        Function:
            Apply pointer movement to the active camera interaction.
        Args:
            model: Current visual model.
            event: Pointer-move event.
        Returns:
            VisualInteractionResult: Interaction result.
        Implementation Logic:
            Middle-button movement pans in screen space and left-button movement
            rotates the camera once movement exceeds the drag threshold.
        """

        state = model.bScene.bInteractionState
        camera = model.bScene.bCameraState
        if state.bActiveButton is None:
            return VisualInteractionResult(bInteractionName="pointer_move_idle")

        delta_x = event.bX - state.bLastX
        delta_y = event.bY - state.bLastY
        total_delta = math.hypot(event.bX - state.bStartX, event.bY - state.bStartY)
        if total_delta >= self.bDragThreshold:
            state.bWasDragged = True

        if state.bActiveButton == "middle":
            camera.bPanX += delta_x * self.bPanSensitivity
            camera.bPanY += delta_y * self.bPanSensitivity
            interaction_name = "pan"
        elif state.bActiveButton == "left" and state.bWasDragged:
            camera.bRotationY += delta_x * self.bRotateSensitivity
            camera.bRotationX += delta_y * self.bRotateSensitivity
            interaction_name = "rotate"
        else:
            interaction_name = "pointer_move_pending_click"

        state.bLastX = event.bX
        state.bLastY = event.bY
        return VisualInteractionResult(
            bDidChangeCamera=interaction_name in {"pan", "rotate"},
            bInteractionName=interaction_name,
        )

    def handlePointerUp(
        self,
        model: VisualModel,
        event: VisualPointerEvent,
        viewport: VisualViewport,
    ) -> VisualInteractionResult:
        """
        Function:
            Finish a pointer interaction and select a node on left-click.
        Args:
            model: Current visual model.
            event: Pointer-up event.
            viewport: Current viewport size.
        Returns:
            VisualInteractionResult: Interaction result with optional hit node.
        Implementation Logic:
            A left-button release without a drag performs hit testing. Drag
            releases simply clear transient pointer state.
        """

        state = model.bScene.bInteractionState
        active_button = state.bActiveButton
        was_dragged = state.bWasDragged
        state.bActiveButton = None
        state.bWasDragged = False

        if active_button == "left" and not was_dragged:
            selected_node = self.hitTest(model=model, viewport=viewport, x=event.bX, y=event.bY)
            selected_node_id = selected_node._id if selected_node is not None else None
            state.bSelectedNodeId = selected_node_id
            model.bSelectionState.bSelectedObjectId = selected_node_id
            log(
                level="debug",
                module="visualizer.interaction",
                message="Pointer click selection resolved.",
                context={"selectedNodeId": selected_node_id},
            )
            return VisualInteractionResult(
                bSelectedNodeId=selected_node_id,
                bSelectedNode=selected_node,
                bInteractionName="select",
            )

        return VisualInteractionResult(bInteractionName="pointer_up")

    def handleWheel(
        self,
        model: VisualModel,
        event: VisualPointerEvent,
        viewport: VisualViewport,
    ) -> VisualInteractionResult:
        """
        Function:
            Apply wheel zoom centered at the mouse position.
        Args:
            model: Current visual model.
            event: Wheel event.
            viewport: Current viewport size.
        Returns:
            VisualInteractionResult: Interaction result.
        Implementation Logic:
            The controller computes the view-plane point under the cursor before
            zooming and adjusts pan so that same point remains under the cursor.
        """

        camera = model.bScene.bCameraState
        if event.bWheelDelta == 0:
            return VisualInteractionResult(bInteractionName="wheel_idle")

        old_zoom = camera.bZoom
        view_x, view_y = self.screenToViewPlane(camera=camera, viewport=viewport, x=event.bX, y=event.bY)
        zoom_factor = self.bZoomStep if event.bWheelDelta > 0 else 1.0 / self.bZoomStep
        new_zoom = max(camera.bMinZoom, min(camera.bMaxZoom, old_zoom * zoom_factor))
        camera.bZoom = new_zoom

        center_x = viewport.bWidth / 2.0
        center_y = viewport.bHeight / 2.0
        camera.bPanX = event.bX - center_x - (view_x * new_zoom)
        camera.bPanY = event.bY - center_y + (view_y * new_zoom)
        return VisualInteractionResult(bDidChangeCamera=True, bInteractionName="zoom")

    def clearSelection(self, model: VisualModel) -> VisualInteractionResult:
        """
        Function:
            Clear generic interaction selection on a visual model.
        Args:
            model: Current visual model.
        Returns:
            VisualInteractionResult: Interaction result.
        Implementation Logic:
            The generic controller clears only renderer-level selected node
            state; concrete visualizers decide how request state is reset.
        """

        model.bScene.bInteractionState.bSelectedNodeId = None
        model.bSelectionState.bSelectedObjectId = None
        return VisualInteractionResult(bInteractionName="clear_selection")

    def hitTest(self, model: VisualModel, viewport: VisualViewport, x: float, y: float) -> VisualSceneNode | None:
        """
        Function:
            Find the topmost visible interactive node under one screen point.
        Args:
            model: Current visual model.
            viewport: Current viewport size.
            x: Screen x coordinate.
            y: Screen y coordinate.
        Returns:
            VisualSceneNode | None: Hit node, if any.
        Implementation Logic:
            Hit testing projects every node through the current camera and
            selects the closest node whose screen distance is inside hit radius.
        """

        best_node: VisualSceneNode | None = None
        best_distance = float("inf")
        for node in model.bScene.bNodeList:
            if not node.bIsVisible or not node.bIsInteractive:
                continue
            screen_x, screen_y, depth = self.projectWorldToScreen(
                camera=model.bScene.bCameraState,
                viewport=viewport,
                position=node.bPosition,
            )
            distance = math.hypot(x - screen_x, y - screen_y)
            if distance <= node.bHitRadius and (distance + depth * 0.001) < best_distance:
                best_distance = distance + depth * 0.001
                best_node = node
        return best_node

    def projectWorldToScreen(
        self,
        camera: VisualCameraState,
        viewport: VisualViewport,
        position: tuple[float, float, float],
    ) -> tuple[float, float, float]:
        """
        Function:
            Project a world-space position into screen coordinates.
        Args:
            camera: Current camera state.
            viewport: Current viewport size.
            position: World-space x, y, z tuple.
        Returns:
            tuple[float, float, float]: Screen x, screen y and depth.
        Implementation Logic:
            A lightweight orbit projection is enough for interaction hit testing
            and can later be replaced by a renderer's exact matrix math.
        """

        x, y, z = position
        cos_y = math.cos(camera.bRotationY)
        sin_y = math.sin(camera.bRotationY)
        rotated_x = (x * cos_y) + (z * sin_y)
        rotated_z = (-x * sin_y) + (z * cos_y)

        cos_x = math.cos(camera.bRotationX)
        sin_x = math.sin(camera.bRotationX)
        rotated_y = (y * cos_x) - (rotated_z * sin_x)
        depth = (y * sin_x) + (rotated_z * cos_x)

        screen_x = (viewport.bWidth / 2.0) + camera.bPanX + (rotated_x * camera.bZoom)
        screen_y = (viewport.bHeight / 2.0) + camera.bPanY - (rotated_y * camera.bZoom)
        return screen_x, screen_y, depth

    @staticmethod
    def screenToViewPlane(
        camera: VisualCameraState,
        viewport: VisualViewport,
        x: float,
        y: float,
    ) -> tuple[float, float]:
        """
        Function:
            Convert a screen coordinate to current view-plane coordinates.
        Args:
            camera: Current camera state.
            viewport: Current viewport size.
            x: Screen x coordinate.
            y: Screen y coordinate.
        Returns:
            tuple[float, float]: View-plane x and y coordinates.
        Implementation Logic:
            Centered zoom only needs view-plane coordinates, so this inverse
            keeps mouse-centered zoom stable without solving full 3D picking.
        """

        view_x = (x - (viewport.bWidth / 2.0) - camera.bPanX) / camera.bZoom
        view_y = -((y - (viewport.bHeight / 2.0) - camera.bPanY) / camera.bZoom)
        return view_x, view_y
