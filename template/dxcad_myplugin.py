# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""A starter DX-CAD plugin: rename it, then add what it registers.

Rename this module and its entry in pyproject.toml together. register() is
handed DX-CAD's Registry (dxcad_sdk.plugin.Registry describes it); each call
adds one thing. Import DX-CAD's own names inside the functions that use them,
so `dxcad-sdk check` can load the module without DX-CAD.
"""

#: What the About action's box is called.
ABOUT_TITLE = "About My Plugin"


def plate(width: float, depth: float, thickness: float):
    """A plain plate, width x depth x thickness, its corner at the origin."""
    from dxcad.model import make_box

    return make_box(width, depth, thickness)


def about_text(registry) -> str:
    """What the About box says: the plugin, and its licence in DX-CAD's own words,
    with the trial's last day (plugin API 2)."""
    trial = registry.trial_end()
    return (
        f"My Plugin\n{registry.licence_words()}\n"
        f"This computer's trial ends {trial.day} {trial:%B %Y}."
    )


def register(registry):
    registry.require(2)
    registry.add_name("plate", plate)

    def about(window) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(window, ABOUT_TITLE, about_text(registry))

    registry.action("about", ABOUT_TITLE, about, toolbar=False)
