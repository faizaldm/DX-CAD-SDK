# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""An example plugin that adds a name to the model language: washer().

After it is installed, every model.py can say

    part("w", washer(20, 10.5, 2))

DX-CAD's own functions are imported inside washer(), where DX-CAD calls it,
so `dxcad-sdk check` can load this module without DX-CAD.
"""


def washer(outer: float, inner: float, thickness: float):
    """A flat washer: `outer` and `inner` diameters, `thickness` high, on the XY plane."""
    from dxcad.model import cut, make_cylinder

    if not 0 < inner < outer or thickness <= 0:
        raise ValueError("a washer needs 0 < inner < outer and a thickness above 0")
    return cut(make_cylinder(outer / 2, thickness), make_cylinder(inner / 2, thickness))


def register(registry):
    registry.require(1)
    registry.add_name("washer", washer)
