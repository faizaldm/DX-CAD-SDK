# SPDX-License-Identifier: Apache-2.0
"""A 1000 x 800 cabinet door bent from 2 mm steel, its return lips mitred at the corners.

1000 x 800 overall, as a drawing gives it: a 45 mm flange on every edge,
each with a 25 mm return lip, both measured to the outside, bent with a
2 mm inside radius. Where two lips meet at a corner they are mitred, cut
back at 45 degrees with a 2 mm gap between them, so no lip runs into the
next. The base is the overall size less a bend radius and a thickness each
side, 992 x 792. Each 45 mm flange with its return is a 37 mm leg and a
21 mm lip, once both bends' setbacks (2 + 2 = 4 each) are taken off, and
each bend allows pi / 2 x (2 + 0.44 x 2) = 4.52389 mm, so every side of the
flat reaches 2 x 4.52389 + 37 + 21 = 67.04779 mm past the base. Its flat is
1126.096 x 926.096 mm, with eight bend lines and the mitres cut in its
corners.

    dxcad run mitred_door.py --output mitred_door.dxcprt
    dxcad flat mitred_door.dxcprt --part door

Tags: sheet
"""

WIDTH = 1000.0
HEIGHT = 800.0
FLANGE = 45.0
RETURN = 25.0
THICKNESS = 2.0
BEND_RADIUS = 2.0
K_FACTOR = 0.44

spec = SheetSpec(THICKNESS, BEND_RADIUS, K_FACTOR)
out = BEND_RADIUS + THICKNESS
base_x, base_y = WIDTH - 2 * out, HEIGHT - 2 * out
door = base_flange([(0, 0), (base_x, 0), (base_x, base_y), (0, base_y)], spec)
for edge in range(4):
    door = flange(
        door,
        edge,
        FLANGE,
        return_length=RETURN,
        length_from="outside",
        corner_treatment="mitre",
    )
part("door", door, color="galvanised")
