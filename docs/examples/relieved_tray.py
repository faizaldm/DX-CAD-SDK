# SPDX-License-Identifier: Apache-2.0
"""A sheet metal tray with two relieved flanges and two holes in its base.

Each flange is inset from both ends of its edge, and `relief=True` cuts a
slot into the base at each inset end so the bend does not tear the corner.
The holes are cut through the base before it is bent. Its flat is 120.000 x
136.786 mm: the base's 80 plus, for each flange, its bend allowance and its
leg. Build it and cut the flat for a laser with:

    dxcad run relieved_tray.py --output relieved_tray.dxcprt
    dxcad flat relieved_tray.dxcprt --part tray

Tags: sheet
"""

LENGTH = 120.0
WIDTH = 80.0
HEIGHT = 25.0
THICKNESS = 1.5
BEND_RADIUS = 1.5
K_FACTOR = 0.44
INSET = 10.0
HOLE = 6.0

spec = SheetSpec(THICKNESS, BEND_RADIUS, K_FACTOR)
holes = [(30.0, WIDTH / 2, HOLE), (LENGTH - 30.0, WIDTH / 2, HOLE)]
tray = base_flange([(0, 0), (LENGTH, 0), (LENGTH, WIDTH), (0, WIDTH)], spec, holes=holes)
for edge in (0, 2):
    tray = flange(tray, edge, HEIGHT, start_inset=INSET, end_inset=INSET, relief=True)

part("tray", tray, color="steel")
