# SPDX-License-Identifier: Apache-2.0
"""A bolt placed in a plate's hole by two mates, as docs/kernel.md shows it.

The bolt is built anywhere; `mate` puts its shank's axis on the hole's and
the underside of its head on the plate's top. 'cylinder 1' is the bolt's
thinnest cylinder, its shank, and '<Z 2' the second plane out facing down,
the head's underside. Make the plate thicker and the bolt rises with it.

Tags: mates, assembly
"""

THICK = 5.0
RADIUS = 3.0

plate = cut(make_box(60, 40, THICK), translate(make_cylinder(RADIUS, THICK), (20, 20, 0)))
part("plate", plate, color="steel")

bolt = fuse(make_cylinder(RADIUS, 20), translate(make_cylinder(5, 4), (0, 0, 20)))
part("bolt", translate(bolt, (100, 50, 30)), color="hardware")
mate("bolt", "cylinder 1", "plate", "hole 1", "concentric")
mate("bolt", "<Z 2", "plate", ">Z", "coincident")
