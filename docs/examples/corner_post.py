# SPDX-License-Identifier: Apache-2.0
"""A door corner post bent from one 1.5 mm sheet, with flanges on its flanges' edges.

Looking down on it: wall B along the bottom, wall A up the left, flange C
turned in off wall A and lip D turned outward off flange C, flange E up the
right with lip F turned in. 130 x 120 x 200 over the walls, every length to
the outside. Each end has two end flanges with a return lip, one bent off
wall B and one off wall A's own end, which is a flange on a flange's edge,
as lip D is on flange C's free edge. The two end flanges are mitred from the
walls' outer corner, the end lip meets lip D on a 45 degree joint as a
picture frame does, and at lip F the corner is square: lip F runs its whole
height and the end lip stops short of it. Every gap is the sheet's 1.5.

Wall B is the base flange, drawn a bend radius and a thickness smaller all
round, since a flange's outside face stands that far beyond the edge it is
bent on. Flange C is given a bend radius short for the same reason: lip D's
bend stands that far beyond flange C's edge, which puts lip D's outside face
C + T from wall A's, where the end flanges' lips are. The flat is one piece
with thirteen bend lines.

    dxcad run corner_post.py --output corner_post.dxcprt
    dxcad flat corner_post.dxcprt --part corner_post

Tags: sheet
"""

H = 200.0
A = 120.0
B = 130.0
C = 25.0
D = 10.0
E = 20.0
F = 10.0
END = 20.0
END_LIP = 10.0
THICKNESS = 1.5
BEND_RADIUS = 1.5
K_FACTOR = 0.44

spec = SheetSpec(THICKNESS, BEND_RADIUS, K_FACTOR)
out = BEND_RADIUS + THICKNESS
# On Plane.XZ the sketch's x is the model's X and its y the model's Z, and
# "down" bends towards +Y, into the post. Edge 0 is the bottom, 1 the right
# (flange E), 2 the top and 3 the left (wall A).
post = base_flange([(out, out), (B - out, out), (B - out, H - out), (out, H - out)], spec, Plane.XZ)
post = flange(post, 3, A, 90, "down", return_length=C - BEND_RADIUS, length_from="outside")
post = flange(post, 1, E, 90, "down", return_length=F, length_from="outside")
for edge in (0, 2):
    post = flange(
        post,
        edge,
        END,
        90,
        "down",
        return_length=END_LIP,
        length_from="outside",
        corner_treatment="square",
    )
# Lip D, on the free edge of wall A's return, turned away from the post's inside.
post = flange(post, (3, "free"), D, 90, "down", length_from="outside")
# Wall A's own ends, at the start and the end of edge 3, turned over the post.
for end in ("start", "end"):
    post = flange(
        post,
        (3, end),
        C + THICKNESS,
        90,
        "up",
        return_length=END_LIP,
        length_from="outside",
        corner_treatment="mitre",
    )
part("corner_post", post, color="galvanised")
