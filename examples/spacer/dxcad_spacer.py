# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""An example plugin with a dialog: Spacer..., which adds a part and its statement.

The window shows a Spacer toolbar and menu. Spacer... asks for the outer and
inner diameters and the length, then adds the part and writes one statement
into the model pane, as one undo entry, so the model rebuilds it. The
statement uses only DX-CAD's own names, so the model runs with or without
this plugin.
"""

FIELDS = [
    ("outer", "Outer diameter (mm)", 12.0),
    ("inner", "Inner diameter (mm)", 6.5),
    ("length", "Length (mm)", 10.0),
]

STATEMENT = (
    'part("{name}", cut(make_cylinder({outer:g} / 2, {length:g}), '
    "make_cylinder({inner:g} / 2, {length:g})))"
)


def add_spacer(window, values):
    """The spacer the dialog describes, added with its statement."""
    from dxcad.model import cut, make_cylinder

    outer, inner, length = (float(values[key]) for key in ("outer", "inner", "length"))
    if not 0 < inner < outer or length <= 0:
        raise ValueError("a spacer needs 0 < inner < outer and a length above 0")
    name = window.free_name("spacer")
    shape = cut(make_cylinder(outer / 2, length), make_cylinder(inner / 2, length))
    window.add_part(name, shape, STATEMENT.format(name=name, outer=outer, inner=inner, length=length))


def register(registry):
    registry.require(1)
    registry.dialog("spacer", "Spacer...", FIELDS, add_spacer)
