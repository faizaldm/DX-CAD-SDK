# SPDX-License-Identifier: Apache-2.0
"""A welded rack frame on castors, from plain parts.

Four posts and three levels of rails, each a 100 x 100 x 4 hollow square
section with square-cut ends, gussets under every rail end, a base plate
under each post and a cap on top, four castors and four lifting eyes. Each
part is a box, a cylinder or a prism, so the bill of materials groups the
identical ones: 12 rails, 24 gussets. Change HEIGHT and the posts grow;
change LEVELS and the lower rails move.

Tags: solid, assembly
"""

WIDTH = 1000.0
DEPTH = 1000.0
HEIGHT = 2000.0
MEMBER = 100.0
WALL = 4.0
LEVELS = (300.0, 1100.0)
PLATE = 150.0
PLATE_THICK = 10.0
CAP_THICK = 6.0
GUSSET = 150.0
GUSSET_THICK = 6.0
WHEEL = 35.0
WHEEL_WIDTH = 30.0
CASTOR = 100.0

POST_LENGTH = HEIGHT - PLATE_THICK - CAP_THICK


def member(length, axis):
    """A hollow square section `length` long along axis 0 (x), 1 (y) or 2 (z), open at both ends."""
    size = [MEMBER, MEMBER, MEMBER]
    size[axis] = length
    along = tuple(1 if i == axis else 0 for i in range(3))
    against = tuple(-1 if i == axis else 0 for i in range(3))
    return hollow_facing(make_box(*size), WALL, [along, against])


def gusset(at, turn):
    """A triangular gusset under a rail end: its corner at `at`, its top leg turned from +x."""
    triangle = extrude(polygon_face([(0, 0), (GUSSET, 0), (0, -GUSSET)]), GUSSET_THICK)
    upright = translate(rotate(triangle, (0, 0, 0), (1, 0, 0), 90), (0, GUSSET_THICK / 2, 0))
    return translate(rotate(upright, (0, 0, 0), (0, 0, 1), turn), at)


def across(radius, start, length, axle):
    """A cylinder across the fork, from y = start for `length`, on the axle at height `axle`."""
    upright = make_cylinder(radius, length, (0, 0, axle + start))
    return rotate(upright, (0, 0, axle), (1, 0, 0), -90)


def castor(x, y):
    """A castor under (x, y): a mounting plate, a swivel, a fork, two axle stubs and a wheel."""
    axle = WHEEL - CASTOR
    side = WHEEL_WIDTH / 2
    leg = -28 - (axle - 10)
    pieces = [
        make_box(120, 120, 8, (-60, -60, -8)),
        make_cylinder(25, 12, (0, 0, -20)),
        make_box(30, 2 * side + 16, 8, (-15, -side - 8, -28)),
        make_box(30, 6, leg, (-15, side + 2, axle - 10)),
        make_box(30, 6, leg, (-15, -side - 8, axle - 10)),
        across(6, side, 2, axle),
        across(6, -side - 2, 2, axle),
        across(WHEEL, -side, WHEEL_WIDTH, axle),
    ]
    return translate(fuse_all(pieces), (x, y, 0))


def eyebolt(x, y):
    """A lifting eye on a square foot, standing on a post's cap at (x, y)."""
    foot = make_box(40, 40, 8, (-20, -20, HEIGHT))
    ring = cut(make_cylinder(30, 10, (0, 0, -5)), make_cylinder(18, 10, (0, 0, -5)))
    ring = translate(rotate(ring, (0, 0, 0), (1, 0, 0), 90), (0, 0, HEIGHT + 8 + 30 - 4))
    return translate(fuse(foot, ring), (x, y, 0))


corners = [(0, 0), (WIDTH - MEMBER, 0), (WIDTH - MEMBER, DEPTH - MEMBER), (0, DEPTH - MEMBER)]
for number, (x, y) in enumerate(corners, start=1):
    px, py = min(x, WIDTH - PLATE), min(y, DEPTH - PLATE)
    part(f"base_plate_{number}", make_box(PLATE, PLATE, PLATE_THICK, (px, py, 0)), color="steel")
    part(f"post_{number}", translate(member(POST_LENGTH, 2), (x, y, PLATE_THICK)), color="dx-red")
    cap = make_box(MEMBER, MEMBER, CAP_THICK, (x, y, HEIGHT - CAP_THICK))
    part(f"cap_{number}", cap, color="steel")
    part(f"castor_{number}", castor(px + PLATE / 2, py + PLATE / 2), color="hardware")
    part(f"eyebolt_{number}", eyebolt(x + MEMBER / 2, y + MEMBER / 2), color="brass")

counts = {"rail": 0, "gusset": 0}


def rail(shape, ends):
    """Register a rail and a gusset under each of its ends, each end an (at, turn)."""
    counts["rail"] += 1
    part(f"rail_{counts['rail']}", shape, color="dx-red")
    for at, turn in ends:
        counts["gusset"] += 1
        part(f"gusset_{counts['gusset']}", gusset(at, turn), color="galvanised")


for top in (*LEVELS, HEIGHT - CAP_THICK):
    z = top - MEMBER
    for y in (0, DEPTH - MEMBER):
        shape = translate(member(WIDTH - 2 * MEMBER, 0), (MEMBER, y, z))
        middle = y + MEMBER / 2
        rail(shape, [((MEMBER, middle, z), 0), ((WIDTH - MEMBER, middle, z), 180)])
    for x in (0, WIDTH - MEMBER):
        shape = translate(member(DEPTH - 2 * MEMBER, 1), (x, MEMBER, z))
        middle = x + MEMBER / 2
        rail(shape, [((middle, MEMBER, z), 90), ((middle, DEPTH - MEMBER, z), -90)])
