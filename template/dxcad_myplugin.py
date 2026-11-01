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
    # Plugin API 3: toolbar="Plates" puts a command on a toolbar of the plugin's
    # own, "My Plugin: Plates", listed beside its main one, its buttons in the
    # order the commands were registered, with no limit to how many; and
    # registry.hide_toolbar("Plates") hides it until the user shows it. A DX-CAD
    # with plugin API 2 has neither, so test first and the plugin loads on both:
    #
    #     if getattr(registry, "api_version", 2) >= 3:
    #         registry.action("plate_box", "Plate", make_plate, toolbar="Plates")
    #         registry.hide_toolbar("Plates")
    #
    # Plugin API 4: registry.toolbar_applies_to(("drawing",), "Plates") shows the
    # toolbar only while a drawing tab is in front; View > Toolbars' tick stays
    # the user's. Test getattr(registry, "api_version", 2) >= 4 before calling it.
    #
    # Plugin API 5: a drawing view may be turned; a Pick's `turn` says by how
    # much, and view_point(view, point, turn) gives the turned (u, v).
