# SPDX-License-Identifier: Apache-2.0
"""A funnel, a thin wall turned about its axis.

A cone on a spout, one wall thick throughout. The wall itself is the sketch:
its outside going up and its inside coming back down, WALL apart measured
across, closed and turned a whole turn about Z. Nothing is hollowed, so
nothing can fail to hollow.

Tags: sketch
"""

MOUTH = 80.0
SPOUT = 16.0
CONE_HEIGHT = 50.0
SPOUT_HEIGHT = 30.0
WALL = 2.0

top = SPOUT_HEIGHT + CONE_HEIGHT

wall = (
    Sketch(Plane.XZ)
    .move_to((SPOUT / 2, 0))
    .line_to((SPOUT / 2, SPOUT_HEIGHT))
    .line_to((MOUTH / 2, top))
    .line_to((MOUTH / 2 - WALL, top))
    .line_to((SPOUT / 2 - WALL, SPOUT_HEIGHT))
    .line_to((SPOUT / 2 - WALL, 0))
    .close()
)

part("funnel", wall.revolve((0, 0, 0), (0, 0, 1)), color="navy")
