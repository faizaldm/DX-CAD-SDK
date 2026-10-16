# SPDX-License-Identifier: Apache-2.0
"""A pipe flange with a bolt circle.

A disc with a bore through its middle and BOLTS holes on a pitch circle. One
drill is made and circular_pattern turns it about the axis, so the count is a
number like any other: change it and every hole moves to suit.

Tags: solid
"""

DIAMETER = 90.0
THICKNESS = 12.0
BORE = 34.0
PITCH_CIRCLE = 65.0
BOLT = 9.0
BOLTS = 6

disc = make_cylinder(DIAMETER / 2, THICKNESS)
bore = make_cylinder(BORE / 2, THICKNESS)
drill = make_cylinder(BOLT / 2, THICKNESS, origin=(PITCH_CIRCLE / 2, 0, 0))
drills = circular_pattern(drill, (0, 0, 0), (0, 0, 1), BOLTS)

part("flange", cut_all(disc, [bore, *drills]), color="galvanised")
