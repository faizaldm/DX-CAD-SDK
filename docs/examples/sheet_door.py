# SPDX-License-Identifier: Apache-2.0
"""A cabinet door bent from 1.5 mm mild steel, with flanges and return lips.

600 x 400 overall, as a drawing gives it: a 20 mm flange on every edge, each
with a 10 mm return lip, both measured to the outside, relieved at their
ends, the corners left open. The base is the overall size less a bend radius
and a thickness each side, 594 x 394. Each 20 mm flange with its return is a
14 mm leg and a 7 mm lip, once both bends' setbacks (1.5 + 1.5 = 3) are
taken off, and each bend allows pi / 2 x (1.5 + 0.44 x 1.5) = 3.39292 mm,
so every side of the flat reaches 2 x 3.39292 + 14 + 7 = 27.78584 mm past
the base. Its flat is 649.572 x 449.572 mm. The long edge at y = 0 carries
two pairs of hinge holes; the handle is a cut-out in the face. It hangs on
the solid door's hinge, door-hinge.dxcasm, used twice and placed by mates.
Copy door-hinge.dxcasm beside this file; `dxcad examples sheet_door` does.

    dxcad run sheet_door.py --output sheet_door.dxcasm
    dxcad flat sheet_door.dxcasm --part panel

Tags: sheet, mates, assembly
"""

WIDTH = 600.0
HEIGHT = 400.0
FLANGE = 20.0
RETURN = 10.0
THICKNESS = 1.5
BEND_RADIUS = 1.5
K_FACTOR = 0.44
HOLE = 4.0
HINGES = (60.0, 474.0)
HANDLE = (120.0, 25.0)

spec = SheetSpec(THICKNESS, BEND_RADIUS, K_FACTOR)
out = BEND_RADIUS + THICKNESS
base_x, base_y = WIDTH - 2 * out, HEIGHT - 2 * out
handle = (base_x / 2, base_y - 60.0, *HANDLE)
panel = base_flange(
    [(0, 0), (base_x, 0), (base_x, base_y), (0, base_y)],
    spec,
    cutouts=[handle],
    corner_treatment="open",
)
# Each hinge's leaf covers a pair of holes 34 apart, half way up the leg.
leg = FLANGE - 2 * out
holes = [(at + offset, leg / 2, HOLE) for at in HINGES for offset in (13.0, 47.0)]
for edge in range(4):
    panel = flange(
        panel,
        edge,
        FLANGE,
        return_length=RETURN,
        length_from="outside",
        start_inset=THICKNESS,
        end_inset=THICKNESS,
        relief=True,
        holes=holes if edge == 0 else (),
    )
part("panel", panel, color="galvanised")

# The hinge turned to lie along the flange, its first leaf over a pair of
# holes, its pin and second leaf above; placed off the door, then mated flush
# against the leg's outside face.
hinge = use("door-hinge.dxcasm", as_group=True)
for name, at in zip(("hinge_left", "hinge_right"), HINGES, strict=True):
    # The leaf's top at the door's top, FLANGE, so the pin clears the return.
    place(name, hinge, at=(at, -40.0, FLANGE), rotate=(0, 90, 0))
    mate(name, ">Y", "panel", "<Y", "coincident")
