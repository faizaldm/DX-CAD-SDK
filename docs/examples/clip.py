# SPDX-License-Identifier: Apache-2.0
"""A cable clip, drawn with arcs.

A C-shaped ring standing on a foot, with a screw hole through the foot beside
it. The whole section is one loop of lines and arcs on the XZ plane: arc_to
names an arc by its radius, which is how a drawing gives one, its sign says
which way the arc turns, and long=True asks for the way round that goes most
of the way about the centre. The sketch is then extruded to the clip's width.

Tags: sketch
"""

CABLE = 10.0
WALL = 2.0
BASE = 3.0
GAP = 6.0
FOOT = 22.0
WIDTH = 12.0
SCREW = 4.0

inner = CABLE / 2
outer = inner + WALL
# The cable rests on the foot, so the ring's centre is one radius above it.
height = BASE + inner
# Where the outside of the ring meets the top of the foot, and where the two
# sides of the gap, GAP apart, meet the outside and the inside of the ring.
meets_foot = (outer**2 - inner**2) ** 0.5
gap_outer = height + (outer**2 - (GAP / 2) ** 2) ** 0.5
gap_inner = height + (inner**2 - (GAP / 2) ** 2) ** 0.5

section = (
    Sketch(Plane.XZ)
    .move_to((-outer, 0))
    .line_to((FOOT, 0))
    .line_to((FOOT, BASE))
    .line_to((meets_foot, BASE))
    .arc_to((GAP / 2, gap_outer), outer)
    .line_to((GAP / 2, gap_inner))
    # Back round the inside the long way: past the bottom of the bore.
    .arc_to((-GAP / 2, gap_inner), inner, long=True)
    .line_to((-GAP / 2, gap_outer))
    .arc_to((-meets_foot, BASE), outer)
    .line_to((-outer, BASE))
    .close()
)
body = section.extrude(WIDTH)

# The XZ plane looks along -Y, so the clip lies between y = -WIDTH and y = 0.
drill = make_cylinder(SCREW / 2, BASE, origin=((outer + FOOT) / 2, -WIDTH / 2, 0))

part("clip", cut(body, drill), color="dx-red")
