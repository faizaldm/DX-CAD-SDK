# SPDX-License-Identifier: Apache-2.0
"""A mounting bracket with four holes: the worked example of docs/examples/bracket.md.

An L in section, drawn on the YZ plane and extruded along X, with a row of
holes through its base. Every name the kernel and the sketch API have is
already in scope. Change a number and run it again.

Tags: sketch
"""

LENGTH = 80.0
DEPTH = 30.0
HEIGHT = 46.0
THICKNESS = 6.0
HOLES = 4
HOLE_DIAMETER = 5.0
INSET = 10.0

section = (
    Sketch(Plane.YZ)
    .move_to((0, 0))
    .line_to((DEPTH, 0))
    .line_to((DEPTH, HEIGHT))
    .line_to((DEPTH - THICKNESS, HEIGHT))
    .line_to((DEPTH - THICKNESS, THICKNESS))
    .line_to((0, THICKNESS))
    .close()
)
body = section.extrude(LENGTH)

pitch = (LENGTH - 2 * INSET) / (HOLES - 1)
drill = make_cylinder(HOLE_DIAMETER / 2, THICKNESS, origin=(INSET, (DEPTH - THICKNESS) / 2, 0))
drills = linear_pattern(drill, (pitch, 0, 0), HOLES)

part("bracket", cut_all(body, drills), color="steel")
