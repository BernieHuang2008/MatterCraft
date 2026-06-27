"""MatterCraft bootstrap entry point."""

from __future__ import annotations

from datetime import datetime
import sys
import tkinter as tk
from tkinter import ttk

from debug_module import DEBUG_MANAGER, log
from matter_core.common import GLOBAL_ID_DISPATCHER
from matter_core.core_classes.atom import AtomLogic
from matter_core.core_classes.bond import BondLogic
from matter_core.core_classes.matter import MatterLogic
from matter_core.core_classes.matter_intmol_interaction import MatterIntmolInteractionLogic
from matter_core.core_classes.mixture import MixtureComponentLogic, MixtureLogic
from matter_core.core_classes.molecule import MoleculeLogic


def build_demo_model() -> dict[str, object]:
    """
    Function:
        Build a small in-memory matter-core demo graph for bootstrap testing.
    Args:
        None.
    Returns:
        dict[str, object]: Demo model objects keyed by role name.
    Implementation Logic:
        The bootstrap model exercises the newly created core classes and ensures
        the debug window has meaningful objects and logs to display.
    """

    hydrogen_a = AtomLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Atom"),
        bAtomicNumber=1,
        bMassNumber=1,
        bCharge=0,
        bElectronConfig={"1s": [1]},
    )
    hydrogen_b = AtomLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Atom"),
        bAtomicNumber=1,
        bMassNumber=1,
        bCharge=0,
        bElectronConfig={"1s": [1]},
    )
    oxygen = AtomLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Atom"),
        bAtomicNumber=8,
        bMassNumber=16,
        bCharge=0,
        bElectronConfig={"1s": [2], "2s": [2], "2p": [2, 1, 1]},
    )

    bond_a = BondLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Bond"),
        bAtomList=[oxygen, hydrogen_a],
        bBondType="covalent",
        bBondOrder="1.0",
        bElectronCount=2,
        bBondLength="9.570000000000e-11",
        bPolarity="8.400000000000e-01",
    )
    bond_b = BondLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Bond"),
        bAtomList=[oxygen, hydrogen_b],
        bBondType="covalent",
        bBondOrder="1.0",
        bElectronCount=2,
        bBondLength="9.570000000000e-11",
        bPolarity="8.400000000000e-01",
    )

    water_molecule = MoleculeLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Molecule"),
        bAtomList={
            hydrogen_a._id: hydrogen_a,
            hydrogen_b._id: hydrogen_b,
            oxygen._id: oxygen,
        },
        bBondList={
            bond_a._id: bond_a,
            bond_b._id: bond_b,
        },
    )

    hydrogen_bond = MatterIntmolInteractionLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("MatterIntmolInteraction"),
        bInteractionType="hydrogenBond",
        bParticipantList=[oxygen.debugSnapshot(), hydrogen_a.debugSnapshot()],
        bInteractionStrength="2.000000000000e+04",
        bInteractionDistance="2.800000000000e-10",
        bDirectionality={"model": "angleSensitive"},
        bGeometry={"angleRad": "3.100000000000e+00"},
        bInteractionModel="custom",
    )

    water_matter = MatterLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Matter"),
        bChemMoleculeList={water_molecule._id: water_molecule},
        bPhyMoleculeGap="2.000000000000e-10",
        bPhyMoleculeArrangement={"model": "liquidLocalCluster"},
        bMatterIntmolInteractionList=[hydrogen_bond],
    )

    water_component = MixtureComponentLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("MixtureComponent"),
        bMatter=water_matter,
        bAmount="5.000000000000e-01",
        bSpatialDistribution="homogeneous",
        bContactRelation={"model": "pairwise", "relationList": []},
    )

    water_mixture = MixtureLogic(
        _id=GLOBAL_ID_DISPATCHER.next_id("Mixture"),
        bMixtureType="solution",
        bMixtureTypeProperty={"state": "bootstrapDemo"},
        bMixtureComponentList=[water_component],
    )

    return {
        "hydrogenA": hydrogen_a,
        "hydrogenB": hydrogen_b,
        "oxygen": oxygen,
        "waterMolecule": water_molecule,
        "waterMatter": water_matter,
        "waterMixture": water_mixture,
    }


def publish_runtime_state(model: dict[str, object], debug_enabled: bool) -> None:
    """
    Function:
        Publish bootstrap runtime state to the shared debug manager.
    Args:
        model: Demo model object map.
        debug_enabled: Whether debug mode is enabled.
    Returns:
        None.
    Implementation Logic:
        Runtime state is centralized in the debug manager so the debug window can
        render session summaries without touching business modules directly.
    """

    mixture = model["waterMixture"]
    molecule = model["waterMolecule"]
    matter = model["waterMatter"]
    DEBUG_MANAGER.update_runtime_state(
        {
            "bootstrap.debugEnabled": debug_enabled,
            "bootstrap.now": datetime.utcnow().isoformat(timespec="seconds"),
            "bootstrap.scene": "matter_core_bootstrap",
            "counts.atom": 3,
            "counts.bond": 2,
            "counts.molecule": 1,
            "counts.matter": 1,
            "counts.mixture": 1,
            "hash.molecule": molecule.hash(),
            "hash.matter": matter.hash(),
            "hash.mixture": mixture.hash(),
        }
    )


def build_main_window(root: tk.Tk, debug_enabled: bool) -> None:
    """
    Function:
        Build the simple bootstrap main window.
    Args:
        root: Tk root window.
        debug_enabled: Whether debug mode is enabled.
    Returns:
        None.
    Implementation Logic:
        The first main window is intentionally small and only demonstrates that
        the core classes and debug window can be initialized together.
    """

    root.title("MatterCraft")
    root.geometry("720x420")

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="MatterCraft Bootstrap", font=("Segoe UI", 20, "bold")).pack(anchor=tk.W)
    ttk.Label(
        frame,
        text="Matter Core base classes and the unified debug module are ready.",
        font=("Segoe UI", 11),
    ).pack(anchor=tk.W, pady=(8, 16))

    mode_text = "ON" if debug_enabled else "OFF"
    ttk.Label(frame, text=f"Debug mode: {mode_text}", font=("Segoe UI", 11)).pack(anchor=tk.W)
    ttk.Label(
        frame,
        text="Run with `debug` to open the Debug window beside this main window.",
        font=("Consolas", 10),
    ).pack(anchor=tk.W, pady=(8, 0))


def main() -> None:
    """
    Function:
        Start the MatterCraft bootstrap application.
    Args:
        None.
    Returns:
        None.
    Implementation Logic:
        The bootstrap entry point parses the ``debug`` command-line flag, builds
        the demo model, initializes the debug module and starts the UI loop.
    """

    debug_enabled = any(argument.lower() == "debug" for argument in sys.argv[1:])
    root = tk.Tk()
    DEBUG_MANAGER.configure(enable_window=debug_enabled, root=root)
    build_main_window(root=root, debug_enabled=debug_enabled)
    model = build_demo_model()
    publish_runtime_state(model=model, debug_enabled=debug_enabled)
    log(level="info", module="logic.bootstrap", message="MatterCraft bootstrap initialized.")
    root.mainloop()


if __name__ == "__main__":
    main()
