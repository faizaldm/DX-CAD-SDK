# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""A starter DX-CAD plugin: rename it, then add what it registers.

Rename this module and its entry in pyproject.toml together. register() is
handed DX-CAD's Registry (dxcad_sdk.plugin.Registry describes it); each call
adds one thing. Import DX-CAD's own names inside the functions that use them,
so `dxcad-sdk check` can load the module without DX-CAD.
"""


def plate(width: float, depth: float, thickness: float):
    """A plain plate, width x depth x thickness, its corner at the origin."""
    from dxcad.model import make_box

    return make_box(width, depth, thickness)


def register(registry):
    registry.require(1)
    registry.add_name("plate", plate)
