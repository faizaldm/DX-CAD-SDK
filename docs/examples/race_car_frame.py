# SPDX-License-Identifier: Apache-2.0
"""A Formula Student race car: tubular spaceframe chassis and running gear.

A single-seat racing car built the way a student team builds one: a welded
spaceframe of round steel tubes running between a named table of node points,
bent front and main roll hoops swept along lines and arcs, a front bulkhead,
side-impact structure and a triangulated engine bay. On it hang the running
gear: double-wishbone suspension with pushrods, rockers and coil-over
dampers, uprights, brakes, four wheels on 13 inch rims, the steering rack and
wheel, the seat, an inline-four engine with its exhaust headers, chain drive,
differential and drive shafts. Every frame tube carries its group's part
number, size and material, so the bill of materials is the cut list. Shows
oriented tubes from a node table, sweeps along a line-and-arc wire (hoops and
headers), lofted coil springs, revolved tyres and rims, booleans, patterns,
mirror, place() for the hubs and identity() for the bill of materials.

As it opens the wishbone and pushrod tubes are drawn solid and each coil
spring with eight straight pieces to a turn, so the model builds quickly.
SOLID_LINKS = False bores the tubes and COIL_STEPS = 12 rounds the springs.

Tags: solid, assembly, showcase
"""

# ------------------------------------------------------------------ constants
TUBE_D = 25.4  # frame tube outside diameter
WALL_THIN = 1.65  # 25.4 x 1.65: bracing, bulkhead support, engine bay
WALL_THICK = 2.4  # 25.4 x 2.4: roll hoops, side impact, bulkhead
HOOP_BEND_R = 90.0  # centreline bend radius of the roll hoops
WISH_D = 19.05  # wishbone tube
WISH_WALL = 1.2
SOLID_LINKS = (
    True  # draw the wishbone and pushrod tubes solid: False bores them, four seconds slower
)
COIL_STEPS = 8  # straight pieces to a turn of each coil spring: 12 draws it rounder

WHEELBASE = 1550.0
TRACK_F = 1240.0
TRACK_R = 1200.0
FRONT_AXLE = 380.0  # station of the front axle behind the front bulkhead
TYRE_R = 260.0  # 20.5 x 7 - 13 slick
TYRE_W = 200.0
RIM_R = 165.0  # 13 inch rim

FRAME_LENGTH = 2080.0  # front bulkhead to rear of the frame
FRAME_Z = 100.0  # height of the bottom rails
BULKHEAD_W = 340.0
BULKHEAD_H = 290.0
FRONT_HOOP_AT = 560.0  # station of the front hoop
FRONT_HOOP_H = 720.0  # top of the front hoop centreline
MAIN_HOOP_AT = 1380.0  # station of the main hoop
MAIN_HOOP_H = 1060.0  # top of the main hoop centreline
MAIN_HOOP_W = 620.0  # main hoop width at the side-impact height
SIDE_IMPACT_Z = 330.0  # upper side-impact member height

FRAME_RED = "#C62828"
SILVER = "#B0BEC5"
ALU = "#90A4AE"
BLACK = "#212121"
TYRE = "#1B1B1B"
RIM = "#37474F"
SPRING = "#F9A825"
CALIPER = "#1565C0"
ENGINE = "#455A64"
CASE = "#607D8B"
EXHAUST = "#BCAAA4"
GOLD = "#FFB300"

REAR_AXLE = FRONT_AXLE + WHEELBASE
SEG = 130.0  # longest straight piece of a swept tube (even meshing)
STEEL = {"material": "25CrMo4 tube, powder coated"}


# ------------------------------------------------------------------ vector maths
def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    return math.sqrt(dot(a, a))


def unit(a):
    return mul(a, 1.0 / norm(a))


def lerp(a, b, t):
    return add(a, mul(sub(b, a), t))


def perp(n):
    """Any unit vector square to n."""
    c = cross(n, (0.0, 0.0, 1.0))
    if norm(c) < 1e-6:
        c = cross(n, (1.0, 0.0, 0.0))
    return unit(c)


def S(s, y, z):
    """World point from a frame station s (mm behind the front bulkhead): the car faces +X."""
    return (-s, y, z)


def flip(p):
    """The same point on the car's other (left, -Y) side."""
    return (p[0], -p[1], p[2])


# ------------------------------------------------------------------ shape helpers
def orient(shape, p, v):
    """Turn a shape built along +Z so its Z axis runs along v, then move its origin to p.

    The rotation is about z x v by the angle between z and v (right-hand rule), which
    carries +Z exactly onto v; a v along -Z is a half turn about X.
    """
    length = norm(v)
    axis = (-v[1], v[0], 0.0)
    if norm(axis) < 1e-9 * length:
        if v[2] < 0:
            shape = rotate(shape, (0, 0, 0), (1, 0, 0), 180)
    else:
        angle = math.degrees(math.acos(max(-1.0, min(1.0, v[2] / length))))
        shape = rotate(shape, (0, 0, 0), axis, angle)
    return translate(shape, p)


def tube(p1, p2, d=TUBE_D, wall=WALL_THIN):
    """A hollow round tube from p1 to p2: a ring square to p2 - p1, swept along the line.

    The line is cut into short collinear pieces (one face each, as on a mitred
    cut list) so the tube meshes evenly along its length.
    """
    n = unit(sub(p2, p1))
    face = Sketch(Plane(p1, n, perp(n))).circle((0, 0), d / 2).circle((0, 0), d / 2 - wall).face()
    return sweep(face, path_wire([p1, p2], 0.0))


def rod(p1, p2, r):
    """A solid round bar from p1 to p2."""
    v = sub(p2, p1)
    return orient(make_cylinder(r, norm(v)), p1, v)


def link_tube(p1, p2, d, wall):
    """A suspension link's tube. With SOLID_LINKS it is drawn as a solid bar, the same outside:
    the fittings fused onto its ends then cross one wall, not two, which is the slow part."""
    return rod(p1, p2, d / 2) if SOLID_LINKS else tube(p1, p2, d, wall)


def disc(centre, axis, r, t):
    """A solid disc of thickness t centred on `centre`, its axis along `axis`."""
    a = unit(axis)
    return orient(make_cylinder(r, t), sub(centre, mul(a, t / 2)), a)


def drill(shape, tools):
    """Cut tools that do not touch one another out of a shape in one cut, not a cut each."""
    return cut(shape, compound(tools))


def join(shape, pieces):
    """Fuse pieces that do not touch one another onto a shape in one fuse."""
    return fuse(shape, compound(pieces))


def line_edges(a, b, step=SEG):
    """The straight run a-b as collinear edges no longer than `step`."""
    k = max(1, int(math.ceil(norm(sub(b, a)) / step)))
    pts = [lerp(a, b, j / k) for j in range(k + 1)]
    return [BRepBuilderAPI_MakeEdge(gp_Pnt(*pts[j]), gp_Pnt(*pts[j + 1])).Edge() for j in range(k)]


def path_wire(points, bend_r):
    """Straight lines through `points` with every inner corner rounded to bend_r."""
    edges, start = [], points[0]
    for i in range(1, len(points) - 1):
        a, p, b = points[i - 1], points[i], points[i + 1]
        u1, u2 = unit(sub(a, p)), unit(sub(b, p))
        half = math.acos(max(-1.0, min(1.0, dot(u1, u2)))) / 2
        t = bend_r / math.tan(half)
        t1, t2 = add(p, mul(u1, t)), add(p, mul(u2, t))
        bis = unit(add(u1, u2))
        centre = add(p, mul(bis, bend_r / math.sin(half)))
        mid = sub(centre, mul(bis, bend_r))
        edges += line_edges(start, t1)
        arc = GC_MakeArcOfCircle(gp_Pnt(*t1), gp_Pnt(*mid), gp_Pnt(*t2)).Value()
        edges.append(BRepBuilderAPI_MakeEdge(arc).Edge())
        start = t2
    edges += line_edges(start, points[-1])
    return make_wire(edges)


def bent_tube(points, bend_r, d=TUBE_D, wall=WALL_THICK):
    """A hollow tube bent through `points`: a ring face swept along lines and arcs."""
    n = unit(sub(points[1], points[0]))
    face = (
        Sketch(Plane(points[0], n, perp(n)))
        .circle((0, 0), d / 2)
        .circle((0, 0), d / 2 - wall)
        .face()
    )
    return sweep(face, path_wire(points, bend_r))


def coil(p1, p2, coil_r, wire_r, turns, per_turn=COIL_STEPS):
    """A coil spring from p1 to p2: a round wire swept along a helix of short lines and arcs."""
    axis = sub(p2, p1)
    w = unit(axis)
    u = perp(w)
    v = cross(w, u)
    n = int(turns * per_turn)
    pts = []
    for k in range(n + 1):
        a = 2 * math.pi * k / per_turn
        pts.append(
            add(
                add(p1, mul(axis, k / n)),
                add(mul(u, coil_r * math.cos(a)), mul(v, coil_r * math.sin(a))),
            )
        )
    n0 = unit(sub(pts[1], pts[0]))
    face = Sketch(Plane(pts[0], n0, perp(n0))).circle((0, 0), wire_r).face()
    return sweep(face, path_wire(pts, coil_r * 0.8))


def plate(points3, thickness):
    """A flat plate through three or more points of one plane, `thickness` thick about it."""
    o = points3[0]
    xd = unit(sub(points3[1], o))
    nrm = unit(cross(sub(points3[1], o), sub(points3[2], o)))
    yd = cross(nrm, xd)
    pts = [(dot(sub(p, o), xd), dot(sub(p, o), yd)) for p in points3]
    face = polygon_face(pts, Plane(sub(o, mul(nrm, thickness / 2)), nrm, xd))
    return extrude(face, thickness, nrm), nrm


def side_profile(points_sz, y0, width):
    """A prism of a (station, z) outline, from y0 across `width` in +Y."""
    pl = Plane((0, y0, 0), (0, 1, 0), (-1, 0, 0))
    return extrude(polygon_face(points_sz, pl), width, (0, 1, 0))


def guarded(fn, shape, *args):
    try:
        return fn(shape, *args)
    except (FilletError, ValueError):
        return shape


# ================================================================== 1 the frame
# Node table: the right-hand (+Y) side; each name ending in R has a mirror in L.
HW_FB = BULKHEAD_W / 2
SIS_W = MAIN_HOOP_W / 2
FH_Z_TOP = FRONT_HOOP_H
MH_SHOULDER_Z = 480.0
NODES = {
    "F1": S(0, HW_FB, FRAME_Z + 10),  # front bulkhead, lower
    "F2": S(0, HW_FB, FRAME_Z + 10 + BULKHEAD_H),  # front bulkhead, upper
    "A1": S(300, HW_FB + 50, FRAME_Z + 5),  # bulkhead support, lower
    "A2": S(300, HW_FB + 50, FRAME_Z + 10 + BULKHEAD_H + 30),  # bulkhead support, upper
    "H1": S(FRONT_HOOP_AT, 250, FRAME_Z),  # front hoop foot
    "H2": S(FRONT_HOOP_AT, 268, SIDE_IMPACT_Z),  # front hoop at side impact
    "H3": S(FRONT_HOOP_AT, 214, FH_Z_TOP - 70),  # front hoop shoulder
    "C1": S(970, SIS_W - 10, FRAME_Z),  # cockpit floor node
    "C2": S(970, SIS_W - 5, SIDE_IMPACT_Z),  # cockpit side-impact node
    "M1": S(MAIN_HOOP_AT, SIS_W - 10, FRAME_Z),  # main hoop foot
    "M2": S(MAIN_HOOP_AT, SIS_W - 6, SIDE_IMPACT_Z),  # main hoop at side impact
    "M3": S(MAIN_HOOP_AT, SIS_W, MH_SHOULDER_Z),  # main hoop, harness bar
    "M4": S(MAIN_HOOP_AT, 250, MAIN_HOOP_H - 120),  # main hoop, brace point
    "B1": S(1760, 240, 450),  # main hoop brace foot
    "E1": S(1760, 260, FRAME_Z + 10),  # engine bay, lower
    "R1": S(FRAME_LENGTH, 220, FRAME_Z + 30),  # rear, lower
    "R2": S(FRAME_LENGTH, 220, 420),  # rear, upper
}
for key in list(NODES):
    NODES[key + "R"] = NODES.pop(key)
    NODES[key + "L"] = flip(NODES[key + "R"])

# Member list: (group, part number, wall, node, node); a group with "*" is built once a side.
GROUPS = {
    "FB": ("front bulkhead", "FR-101", WALL_THICK),
    "FBS": ("bulkhead support", "FR-102", WALL_THIN),
    "SIS": ("side impact", "FR-103", WALL_THICK),
    "FLR": ("floor", "FR-104", WALL_THIN),
    "CKP": ("cockpit rail", "FR-105", WALL_THIN),
    "MHB": ("main hoop brace", "FR-106", WALL_THICK),
    "EB": ("engine bay", "FR-107", WALL_THIN),
    "RR": ("rear", "FR-108", WALL_THIN),
}
SIDE_MEMBERS = [
    ("FB", "F1", "F2"),
    ("FBS", "F1", "A1"),
    ("FBS", "F2", "A2"),
    ("FBS", "A1", "A2"),
    ("FBS", "F2", "A1"),
    ("FBS", "A1", "H1"),
    ("FBS", "A2", "H3"),
    ("FBS", "A2", "H2"),
    ("FBS", "A1", "H2"),
    ("SIS", "H1", "C1"),
    ("SIS", "C1", "M1"),
    ("SIS", "H2", "C2"),
    ("SIS", "C2", "M2"),
    ("SIS", "H1", "C2"),
    ("SIS", "C2", "M1"),
    ("SIS", "C1", "C2"),
    ("CKP", "H3", "M3"),
    ("MHB", "M4", "B1"),
    ("MHB", "B1", "M3"),
    ("EB", "M1", "E1"),
    ("EB", "M2", "E1"),
    ("EB", "E1", "B1"),
    ("EB", "M3", "B1"),
    ("RR", "E1", "R1"),
    ("RR", "B1", "R2"),
    ("RR", "R1", "R2"),
    ("RR", "E1", "R2"),
]
CROSS_MEMBERS = [
    ("FB", "F1R", "F1L"),
    ("FB", "F2R", "F2L"),
    ("FB", "F1R", "F2L"),
    ("FBS", "A1R", "A1L"),
    ("FBS", "A2R", "A2L"),
    ("FLR", "H1R", "H1L"),
    ("FLR", "C1R", "C1L"),
    ("FLR", "M1R", "M1L"),
    ("FLR", "H1R", "C1L"),
    ("FLR", "C1L", "M1R"),
    ("CKP", "M3R", "M3L"),
    ("MHB", "B1R", "B1L"),
    ("EB", "E1R", "E1L"),
    ("RR", "R1R", "R1L"),
    ("RR", "R2R", "R2L"),
    ("RR", "R1L", "R2R"),
]

members = []
for g, a, b in SIDE_MEMBERS:
    for side in "RL":
        members.append((g, a + side, b + side))
members += CROSS_MEMBERS

count = {}
for g, a, b in members:
    label, pn, wall = GROUPS[g]
    count[g] = count.get(g, 0) + 1
    name = f"tube_{g.lower()}_{count[g]:02d}_{a}_{b}"
    shape = tube(NODES[a], NODES[b], TUBE_D, wall)
    part(name, shape, color=FRAME_RED)
    identity(
        name,
        part_number=f"{pn}-{count[g]:02d}",
        properties={
            "group": label,
            "size": f"{TUBE_D} x {wall}",
            "length": f"{norm(sub(NODES[a], NODES[b])):.0f}",
            **STEEL,
        },
    )


# The roll hoops: one bent tube each, swept along lines and arcs.
FA = FRONT_HOOP_AT
front_pts = [
    S(FA, -250, FRAME_Z - 5),
    S(FA, -276, SIDE_IMPACT_Z + 80),
    S(FA, -190, FRONT_HOOP_H),
    S(FA, 190, FRONT_HOOP_H),
    S(FA, 276, SIDE_IMPACT_Z + 80),
    S(FA, 250, FRAME_Z - 5),
]
part(
    "front_hoop",
    bent_tube(front_pts, HOOP_BEND_R),
    color=FRAME_RED,
    part_number="FR-110",
    properties={"group": "front roll hoop", "size": f"{TUBE_D} x {WALL_THICK}", **STEEL},
)

main_pts = [
    S(MAIN_HOOP_AT, -(SIS_W - 10), FRAME_Z - 5),
    S(MAIN_HOOP_AT, -SIS_W - 6, MH_SHOULDER_Z),
    S(MAIN_HOOP_AT, -210, MAIN_HOOP_H),
    S(MAIN_HOOP_AT, 210, MAIN_HOOP_H),
    S(MAIN_HOOP_AT, SIS_W + 6, MH_SHOULDER_Z),
    S(MAIN_HOOP_AT, SIS_W - 10, FRAME_Z - 5),
]
part(
    "main_hoop",
    bent_tube(main_pts, HOOP_BEND_R * 1.4),
    color=FRAME_RED,
    part_number="FR-111",
    properties={"group": "main roll hoop", "size": f"{TUBE_D} x {WALL_THICK}", **STEEL},
)

# Node gussets where the main hoop braces land and at the hoop feet.
for side in "RL":
    for a, b, c in (("M4", "B1", "M3"), ("M1", "C1", "C2"), ("H1", "A1", "H2")):
        pa, pb, pc = NODES[a + side], NODES[b + side], NODES[c + side]
        g, _ = plate([pa, lerp(pa, pb, 0.22), lerp(pa, pc, 0.22)], 3.0)
        part(
            f"gusset_{a.lower()}_{side}",
            g,
            color=FRAME_RED,
            part_number="FR-120",
            properties={"group": "node gusset", "size": "3 mm plate", **STEEL},
        )


# ================================================================== 2 suspension
def corner(axle_s, track, front):
    """Right-hand corner: returns a dict of named shapes (in world, +Y side)."""
    yw = track / 2
    out = {}
    lbj = S(axle_s, yw - 55, TYRE_R - 125)  # lower ball joint
    ubj = S(axle_s, yw - 75, TYRE_R + 125)  # upper ball joint
    if front:
        lf, lr = S(axle_s - 150, 225, FRAME_Z + 12), S(axle_s + 150, 245, FRAME_Z + 8)
        uf, ur = S(axle_s - 130, 235, 330), S(axle_s + 140, 262, 320)
        rocker = S(axle_s + 10, 205, 470)
        dmount = S(110, 150, FRAME_Z + BULKHEAD_H + 10)
    else:
        lf, lr = S(axle_s - 160, 248, FRAME_Z + 18), S(axle_s + 130, 225, FRAME_Z + 27)
        uf, ur = S(axle_s - 170, 238, 345), S(axle_s + 130, 222, 340)
        rocker = S(axle_s - 10, 222, 470)
        dmount = S(axle_s - 260, 150, 470)
    for nm, f, r, bj in (("lower", lf, lr, lbj), ("upper", uf, ur, ubj)):
        housing = disc(bj, (0, 0, 1), 15, 26)
        arm = fuse_all(
            [housing, link_tube(f, bj, WISH_D, WISH_WALL), link_tube(r, bj, WISH_D, WISH_WALL)]
        )
        arm = join(arm, [disc(f, (1, 0, 0), 11, 22), disc(r, (1, 0, 0), 11, 22)])
        out[f"wishbone_{nm}"] = arm
        out[f"bracket_{nm}_f"] = make_box(30, 26, 26, sub(f, (15, 13, 13)))
        out[f"bracket_{nm}_r"] = make_box(30, 26, 26, sub(r, (15, 13, 13)))
    # upright: a machined body between the ball joints, a spindle boss and a steering or toe arm
    mid = lerp(lbj, ubj, 0.5)
    body = fuse_all(
        [
            rod(lbj, ubj, 22),
            disc(add(mid, (0, 18, 0)), (0, 1, 0), 58, 34),
            make_box(70, 30, 120, sub(mid, (35, 5, 60))),
        ]
    )
    arm_end = S(axle_s + 85, yw - 95, TYRE_R - 60)
    body = fuse(body, rod(add(mid, (0, 0, -40)), arm_end, 9))
    out["upright"] = body
    # pushrod from the lower wishbone near the ball joint up to the rocker
    pr_low = lerp(lerp(lf, lr, 0.5), lbj, 0.86)
    pr_low = add(pr_low, (0, 0, 18))
    pr_top = add(rocker, mul(unit(sub(pr_low, rocker)), 60))
    out["pushrod"] = join(
        link_tube(pr_low, pr_top, 16, 1.2),
        [disc(pr_low, (1, 0, 0), 9, 16), disc(pr_top, (1, 0, 0), 9, 16)],
    )
    d_end = add(rocker, mul(unit(sub(dmount, rocker)), 55))
    rk, n_rk = plate([rocker, pr_top, d_end], 8.0)
    bosses = [disc(p, n_rk, r, 14) for p, r in ((rocker, 16), (pr_top, 11), (d_end, 11))]
    out["rocker"] = fuse_all([rk] + bosses)
    # coil-over damper from the rocker to its mount
    dv = sub(dmount, d_end)
    dl = norm(dv)
    w = unit(dv)
    body_a = add(d_end, mul(w, 0.42 * dl))
    out["damper_body"] = fuse_all(
        [
            rod(body_a, dmount, 17),
            disc(dmount, n_rk, 10, 22),
            rod(add(body_a, mul(w, 18)), add(body_a, mul(w, 30)), 26),
        ]
    )
    out["damper_shaft"] = fuse_all(
        [rod(d_end, add(body_a, mul(w, 5)), 7), disc(d_end, n_rk, 10, 20)]
    )
    out["spring"] = coil(add(d_end, mul(w, 0.12 * dl)), add(body_a, mul(w, 22)), 24, 4.2, 5)
    # spindle, hub and brake: the wheel side
    out["link"] = rod(arm_end, S(axle_s + 85, 230 if front else 240, TYRE_R - 60), 7)
    out["link_end"] = disc(S(axle_s + 85, 230 if front else 240, TYRE_R - 60), (0, 0, 1), 11, 18)
    return out


SUSP_COLORS = {
    "wishbone_lower": SILVER,
    "wishbone_upper": SILVER,
    "bracket_lower_f": FRAME_RED,
    "bracket_lower_r": FRAME_RED,
    "bracket_upper_f": FRAME_RED,
    "bracket_upper_r": FRAME_RED,
    "upright": ALU,
    "pushrod": SILVER,
    "rocker": BLACK,
    "damper_body": BLACK,
    "damper_shaft": "#ECEFF1",
    "spring": SPRING,
    "link": SILVER,
    "link_end": BLACK,
}
SUSP_PN = {
    "wishbone_lower": "SU-301",
    "wishbone_upper": "SU-302",
    "bracket_lower_f": "FR-130",
    "bracket_lower_r": "FR-130",
    "bracket_upper_f": "FR-130",
    "bracket_upper_r": "FR-130",
    "upright": "SU-310",
    "pushrod": "SU-320",
    "rocker": "SU-321",
    "damper_body": "SU-330",
    "damper_shaft": "SU-331",
    "spring": "SU-332",
    "link": "SU-340",
    "link_end": "SU-341",
}
SUSP_MAT = {
    "wishbone_lower": "25CrMo4 tube 19.05 x 1.2",
    "wishbone_upper": "25CrMo4 tube 19.05 x 1.2",
    "upright": "7075-T6 billet",
    "rocker": "7075-T6, black anodised",
    "spring": "54SiCr6 spring wire",
    "pushrod": "25CrMo4 tube 16 x 1.2",
}

for axle_s, track, front, tag in (
    (FRONT_AXLE, TRACK_F, True, "F"),
    (REAR_AXLE, TRACK_R, False, "R"),
):
    parts_r = corner(axle_s, track, front)
    for key, shape in parts_r.items():
        nm = key.replace("link", "tie_rod" if front else "toe_link")
        for side, sh in (("R", shape), ("L", mirror(shape, (0, 0, 0), (0, 1, 0)))):
            part(
                f"{nm}_{tag}{side}",
                sh,
                color=SUSP_COLORS[key],
                part_number=SUSP_PN[key] + ("F" if front else "R"),
                properties={"material": SUSP_MAT.get(key, "steel")},
            )


# ================================================================== 3 wheels
def tyre_shape():
    pts = []
    rc, a = (RIM_R + TYRE_R) / 2 - 6, (TYRE_R - RIM_R) / 2 + 6
    b = TYRE_W / 2
    for k in range(48):
        t = 2 * math.pi * k / 48
        c, s_ = math.cos(t), math.sin(t)
        pts.append(
            (rc + a * math.copysign(abs(c) ** 0.45, c), b * math.copysign(abs(s_) ** 0.3, s_))
        )
    return revolve(polygon_face(pts, Plane.XZ), (0, 0, 0), (0, 0, 1))


def rim_shape():
    w = TYRE_W / 2 - 8
    prof = [
        (RIM_R - 6, -w),
        (RIM_R + 12, -w),
        (RIM_R + 12, -w + 6),
        (RIM_R, -w + 14),
        (RIM_R, w - 14),
        (RIM_R + 12, w - 6),
        (RIM_R + 12, w),
        (RIM_R - 6, w),
    ]
    return revolve(polygon_face(prof, Plane.XZ), (0, 0, 0), (0, 0, 1))


def centre_shape():
    z0 = TYRE_W / 2 - 60
    hub = make_cylinder(52, 26, (0, 0, z0))
    spoke = polygon_face(
        [(40, -14), (RIM_R - 3, -9), (RIM_R - 3, 9), (40, 14)], Plane.XY.offset(z0 + 4)
    )
    spoke = extrude(spoke, 16)
    spokes = circular_pattern(spoke, (0, 0, 0), (0, 0, 1), 10)
    shape = fuse_all([hub] + spokes)
    return cut(shape, make_cylinder(20, 40, (0, 0, z0 - 5)))


def nut_shape():
    z0 = TYRE_W / 2 - 34
    hexagon = polygon_face(
        [
            (30 * math.cos(math.radians(60 * k)), 30 * math.sin(math.radians(60 * k)))
            for k in range(6)
        ],
        Plane.XY.offset(z0),
    )
    return fuse(extrude(hexagon, 18), make_cylinder(19, 26, (0, 0, z0)))


def disc_shape():
    z0 = -24.0
    d = cut(make_cylinder(118, 6, (0, 0, z0)), make_cylinder(58, 6, (0, 0, z0)))
    holes = circular_pattern(make_cylinder(4, 6, (92, 0, z0)), (0, 0, 0), (0, 0, 1), 18)
    holes += circular_pattern(make_cylinder(4, 6, (104, 0, z0)), (0, 0, 0), (0, 0, 1), 18, 360)
    holes = holes[:18] + [rotate(h, (0, 0, 0), (0, 0, 1), 10) for h in holes[18:]]
    carrier = cut(make_cylinder(62, 10, (0, 0, z0 - 2)), make_cylinder(30, 10, (0, 0, z0 - 2)))
    return fuse(drill(d, holes), carrier)


def caliper_shape():
    body = make_box(70, 34, 44, (-35, 92, -43))
    return rotate(guarded(fillet_all, body, 5.0), (0, 0, 0), (0, 0, 1), 40)


WHEEL_PARTS = (
    ("tyre", tyre_shape(), TYRE, "WH-401", "slick 20.5 x 7.0-13"),
    ("rim", rim_shape(), RIM, "WH-402", "magnesium, painted"),
    ("wheel_centre", centre_shape(), RIM, "WH-403", "magnesium casting"),
    ("centre_nut", nut_shape(), GOLD, "WH-404", "7075-T6, gold anodised"),
    ("brake_disc", disc_shape(), "#9E9E9E", "BR-501", "cast iron"),
    ("caliper", caliper_shape(), CALIPER, "BR-502", "aluminium, anodised"),
)
for axle_s, track, tag in ((FRONT_AXLE, TRACK_F, "F"), (REAR_AXLE, TRACK_R, "R")):
    for side, sgn in (("R", 1), ("L", -1)):
        at = S(axle_s, sgn * track / 2, TYRE_R)
        for key, shape, col, pn, mat in WHEEL_PARTS:
            name = f"{key}_{tag}{side}"
            sh = rotate(shape, (0, 0, 0), (1, 0, 0), -90 * sgn)
            if key == "caliper" and tag == "F":
                sh = rotate(sh, (0, 0, 0), (0, 1, 0), 180)
            part(name, translate(sh, at), color=col, part_number=pn, properties={"material": mat})
        # the hub and spindle are placed: one shape, put in at each corner
        hub = fuse(make_cylinder(32, 80, (0, 0, -70)), make_cylinder(48, 12, (0, 0, -16)))
        place(f"hub_{tag}{side}", hub, at=at, rotate=(-90 * sgn, 0, 0))
        identity(f"hub_{tag}{side}", part_number="WH-405", properties={"material": "4340 steel"})

# ================================================================== 4 steering, seat, cockpit
rack_s, rack_z = FRONT_AXLE + 85, TYRE_R - 60
part(
    "steering_rack",
    fuse_all(
        [
            rod(S(rack_s, -160, rack_z), S(rack_s, 160, rack_z), 16),
            disc(S(rack_s, 40, rack_z), (0, 1, 0), 28, 70),
            rod(S(rack_s, -238, rack_z), S(rack_s, 238, rack_z), 8),
        ]
    ),
    color=ALU,
    part_number="ST-601",
    properties={"material": "aluminium housing, steel rack"},
)
col_a, col_b = S(rack_s, 40, rack_z + 20), S(800, 0, 505)
part(
    "steering_column",
    fuse(rod(col_a, col_b, 10), rod(lerp(col_a, col_b, 0.4), lerp(col_a, col_b, 0.42), 16)),
    color=SILVER,
    part_number="ST-602",
    properties={"material": "steel tube"},
)
cv = unit(sub(col_b, col_a))
sw = orient(
    fuse_all(
        [
            make_cylinder(40, 30, (0, 0, -10)),
            rod((-128, 0, 5), (128, 0, 5), 10),
            make_torus(130, 13),
        ]
    ),
    add(col_b, mul(cv, 25)),
    cv,
)
part(
    "steering_wheel",
    sw,
    color=BLACK,
    part_number="ST-603",
    properties={"material": "carbon, suede grips"},
)
part("quick_release", rod(col_b, add(col_b, mul(cv, 22)), 22), color=GOLD, part_number="ST-604")

SEAT_SHELL = [
    (860, 175),
    (930, 150),
    (1240, 108),
    (1300, 112),
    (1370, 520),
    (1356, 524),
    (1288, 128),
    (1240, 124),
    (935, 166),
    (868, 188),
]
SEAT_SIDE = [
    (930, 150),
    (1240, 108),
    (1300, 112),
    (1370, 520),
    (1320, 500),
    (1250, 260),
    (1200, 235),
    (930, 215),
]
seat = fuse_all(
    [
        side_profile(SEAT_SHELL, -175, 350),
        side_profile(SEAT_SIDE, -185, 12),
        side_profile(SEAT_SIDE, 173, 12),
    ]
)
part("seat", seat, color="#263238", part_number="CK-701", properties={"material": "carbon/foam"})
firewall = [
    S(MAIN_HOOP_AT + 25, -SIS_W + 20, FRAME_Z + 10),
    S(MAIN_HOOP_AT + 25, SIS_W - 20, FRAME_Z + 10),
    S(MAIN_HOOP_AT + 25, SIS_W - 10, MH_SHOULDER_Z + 20),
    S(MAIN_HOOP_AT + 25, -SIS_W + 10, MH_SHOULDER_Z + 20),
]
part(
    "firewall",
    plate(firewall, 2.0)[0],
    color=ALU,
    part_number="CK-702",
    properties={"material": "aluminium sheet 1 mm on 1 mm Nomex"},
)

# ================================================================== 5 engine and drivetrain
ENG_S, ENG_Z = 1440.0, FRAME_Z + 40
crank = make_box(260, 400, 180, (-(ENG_S + 260), -200, ENG_Z))
crank = guarded(fillet, crank, 18.0, edges_parallel_to(crank, (0, 1, 0)))
sump = make_box(200, 300, 60, (-(ENG_S + 230), -150, ENG_Z - 30))
part(
    "engine_crankcase",
    fuse(crank, sump),
    color=ENGINE,
    part_number="EN-801",
    properties={"material": "cast aluminium", "engine": "600 cc inline four"},
)
# cylinder block leaning forward 25 degrees, with cooling fins
blk = make_box(150, 360, 170, (-(ENG_S + 205), -180, ENG_Z + 170))
fins = linear_pattern(make_box(170, 380, 4, (-(ENG_S + 215), -190, ENG_Z + 200)), (0, 0, 22), 6)
blk = join(blk, fins)
blk = rotate(blk, S(ENG_S + 130, 0, ENG_Z + 180), (0, 1, 0), 25)
part(
    "engine_block", blk, color=CASE, part_number="EN-802", properties={"material": "cast aluminium"}
)
head = rotate(
    make_box(160, 380, 70, (-(ENG_S + 210), -190, ENG_Z + 345)),
    S(ENG_S + 130, 0, ENG_Z + 180),
    (0, 1, 0),
    25,
)
part(
    "cylinder_head",
    head,
    color=ENGINE,
    part_number="EN-803",
    properties={"material": "cast aluminium"},
)
cover = rotate(
    guarded(fillet_all, make_box(130, 340, 40, (-(ENG_S + 195), -170, ENG_Z + 412)), 12.0),
    S(ENG_S + 130, 0, ENG_Z + 180),
    (0, 1, 0),
    25,
)
part(
    "cam_cover",
    cover,
    color="#1C1C1C",
    part_number="EN-804",
    properties={"material": "magnesium, painted"},
)
# intake plenum and four runners rising behind the head
plenum = rod(S(ENG_S + 300, -170, ENG_Z + 470), S(ENG_S + 300, 170, ENG_Z + 470), 45)
runners = [
    rod(S(ENG_S + 205, y, ENG_Z + 400), S(ENG_S + 300, y, ENG_Z + 470), 18)
    for y in (-135, -45, 45, 135)
]
part(
    "intake_plenum",
    fuse_all([plenum] + runners),
    color="#212121",
    part_number="EN-810",
    properties={"material": "carbon"},
)
part(
    "throttle_body",
    rod(S(ENG_S + 300, 170, ENG_Z + 470), S(ENG_S + 300, 250, ENG_Z + 470), 26),
    color=ALU,
    part_number="EN-811",
)
part(
    "air_restrictor",
    orient(make_cone(26, 12, 80), S(ENG_S + 300, 250, ENG_Z + 470), (0, 1, 0)),
    color=ALU,
    part_number="EN-812",
    properties={"note": "20 mm restrictor"},
)
# gearbox and output sprocket
gbox = make_box(150, 330, 150, (-(ENG_S + 400), -165, ENG_Z + 10))
part(
    "gearbox",
    guarded(fillet, gbox, 15.0, edges_parallel_to(gbox, (0, 1, 0))),
    color=CASE,
    part_number="EN-820",
    properties={"material": "cast aluminium"},
)


def sprocket(teeth, r, t):
    pts = []
    for k in range(teeth * 2):
        a = math.pi * k / teeth
        rr = r + (5 if k % 2 == 0 else -3)
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    face = polygon_face(pts, Plane((0, 0, 0), (0, 1, 0), (1, 0, 0)))
    return cut(extrude(face, t, (0, 1, 0)), rod((0, -1, 0), (0, t + 1, 0), r * 0.35))


out_c = S(ENG_S + 340, -175, ENG_Z + 60)
diff_c = S(REAR_AXLE, -175, TYRE_R)
part("sprocket_front", translate(sprocket(13, 34, 8), out_c), color="#424242", part_number="DT-901")
part(
    "sprocket_rear", translate(sprocket(40, 104, 8), diff_c), color="#424242", part_number="DT-902"
)
# chain: an open belt round both sprockets, as one swept ring
cdx, cdz = diff_c[0] - out_c[0], diff_c[2] - out_c[2]
cl = math.hypot(cdx, cdz)
ca = math.atan2(cdz, cdx)
r1, r2 = 36.0, 106.0
beta = math.asin((r2 - r1) / cl)
outline = []
for k in range(25):
    a = ca + math.pi / 2 + beta + (math.pi - 2 * beta) * k / 24
    outline.append((out_c[0] + r1 * math.cos(a), out_c[2] + r1 * math.sin(a)))
for k in range(41):
    a = ca - math.pi / 2 - beta + (math.pi + 2 * beta) * k / 40
    outline.append((diff_c[0] + r2 * math.cos(a), diff_c[2] + r2 * math.sin(a)))
pl = Plane((0, -186, 0), (0, -1, 0), (1, 0, 0))
outline_xy = [(x, z) for x, z in outline]
chain_out = extrude(polygon_face(outline_xy, pl), 12, (0, 1, 0))
inset = []
for x, z in outline:
    c = out_c if math.hypot(x - out_c[0], z - out_c[2]) < r1 + 1 else diff_c
    rr = math.hypot(x - c[0], z - c[2])
    k = (rr - 8) / rr
    inset.append((c[0] + (x - c[0]) * k, c[2] + (z - c[2]) * k))
chain = cut(chain_out, extrude(polygon_face(inset, pl), 12, (0, 1, 0)))
part("chain", chain, color="#616161", part_number="DT-903", properties={"size": "520 pitch"})
part(
    "differential",
    fuse_all(
        [
            disc(S(REAR_AXLE, 0, TYRE_R), (0, 1, 0), 78, 150),
            disc(S(REAR_AXLE, 0, TYRE_R), (0, 1, 0), 55, 260),
        ]
    ),
    color=ALU,
    part_number="DT-910",
    properties={"material": "Drexler FS limited-slip"},
)
for side, sgn in (("R", 1), ("L", -1)):
    a, b = S(REAR_AXLE, sgn * 130, TYRE_R), S(REAR_AXLE, sgn * (TRACK_R / 2 - 75), TYRE_R)
    part(
        f"driveshaft_{side}",
        rod(a, b, 13),
        color=SILVER,
        part_number="DT-920",
        properties={"material": "300M steel"},
    )
    for k, (p, r) in enumerate(((lerp(a, b, 0.05), 34), (lerp(a, b, 0.95), 32))):
        boot = orient(make_cone(r, 15, 60), p, mul((0, 1, 0), sgn))
        part(f"cv_boot_{side}{k + 1}", boot, color=BLACK, part_number="DT-921")
    plate_pts = [
        S(REAR_AXLE - 120, sgn * 110, FRAME_Z + 40),
        S(REAR_AXLE + 140, sgn * 110, FRAME_Z + 40),
        S(REAR_AXLE + 140, sgn * 110, 420),
        S(REAR_AXLE - 60, sgn * 110, 420),
    ]
    dp = plate(plate_pts, 8.0)[0]
    part(
        f"diff_carrier_{side}",
        cut(dp, disc(S(REAR_AXLE, sgn * 110, TYRE_R), (0, 1, 0), 60, 20)),
        color=ALU,
        part_number="DT-911",
        properties={"material": "7075-T6 plate"},
    )

# exhaust: four headers swept along lines and arcs into a collector and silencer
COLLECT = S(1990, 255, 300)
for k, y in enumerate((-135, -45, 45, 135)):
    port = S(ENG_S + 20, y, ENG_Z + 360)
    pts = [
        port,
        S(ENG_S - 30, y, ENG_Z + 300),
        S(ENG_S - 10, 300 - 0.15 * y, ENG_Z + 160 + 0.3 * y),
        S(ENG_S + 260, 300 - 0.12 * y, 260 + 0.2 * y),
        S(1940, 262, 300 + 0.05 * y),
    ]
    try:
        hdr = bent_tube(pts, 45.0, 38.0, 1.5)
    except (SweepError, ValueError):
        hdr = fuse_all([tube(pts[i], pts[i + 1], 38.0, 1.5) for i in range(len(pts) - 1)])
    part(
        f"header_{k + 1}",
        hdr,
        color=EXHAUST,
        part_number="EX-951",
        properties={"material": "321 stainless"},
    )
part(
    "collector",
    orient(make_cone(42, 30, 90), S(1930, 262, 300), (-1, 0, 0)),
    color=EXHAUST,
    part_number="EX-952",
)
part(
    "silencer",
    fuse(
        rod(S(2010, 262, 300), S(2290, 262, 300), 55), rod(S(2290, 262, 300), S(2330, 262, 300), 25)
    ),
    color="#9E9E9E",
    part_number="EX-953",
    properties={"material": "titanium"},
)

# radiator in the right side pod, with its fan
rad = make_box(220, 36, 260, (-(MAIN_HOOP_AT - 60), SIS_W + 40, 170))
rad = join(
    rad,
    linear_pattern(make_box(232, 44, 3, (-(MAIN_HOOP_AT - 54), SIS_W + 36, 180)), (0, 0, 12), 21),
)
rad = rotate(rad, S(MAIN_HOOP_AT - 170, SIS_W + 60, 300), (0, 0, 1), 25)
part(
    "radiator",
    rad,
    color="#37474F",
    part_number="CL-960",
    properties={"material": "aluminium core"},
)
part(
    "radiator_fan",
    disc(S(MAIN_HOOP_AT - 175, SIS_W + 34, 300), (0.42, 0.9, 0), 100, 26),
    color=BLACK,
    part_number="CL-961",
)


# ========================================================= 6 front: impact attenuator and pedal box
def rect_wire(s, hw, z0, z1):
    pts = [(-hw, z0), (hw, z0), (hw, z1), (-hw, z1)]
    return wires(polygon_face(pts, Plane(S(s, 0, 0), (-1, 0, 0), (0, -1, 0))))[0]


fb_z0, fb_z1 = FRAME_Z + 10, FRAME_Z + 10 + BULKHEAD_H
aip_s = -(TUBE_D / 2 + 2.5)  # the plate bolts flat on the front face of the bulkhead tubes
part(
    "anti_intrusion_plate",
    plate(
        [
            S(aip_s, -HW_FB - 15, fb_z0 - 15),
            S(aip_s, HW_FB + 15, fb_z0 - 15),
            S(aip_s, HW_FB + 15, fb_z1 + 15),
            S(aip_s, -HW_FB - 15, fb_z1 + 15),
        ],
        4.0,
    )[0],
    color=ALU,
    part_number="FR-140",
    properties={"material": "aluminium 4 mm"},
)
part(
    "impact_attenuator",
    loft(
        [
            rect_wire(aip_s - 2.5, 150, fb_z0, fb_z0 + 200),
            rect_wire(aip_s - 202.5, 95, fb_z0 + 30, fb_z0 + 160),
        ]
    ),
    color="#FBC02D",
    part_number="FR-141",
    properties={"material": "aluminium honeycomb, standard attenuator"},
)
part(
    "pedal_tray",
    make_box(260, 280, 6, (-320, -140, FRAME_Z + 14)),
    color=ALU,
    part_number="PD-150",
    properties={"material": "7075-T6 plate"},
)
for k, (nm, y, h) in enumerate((("brake_pedal", -50, 230), ("throttle_pedal", 70, 210))):
    pivot = S(300, y, FRAME_Z + 30)
    top = S(170, y, FRAME_Z + 30 + h)
    arm = fuse_all(
        [
            disc(pivot, (0, 1, 0), 14, 26),
            rod(pivot, top, 9),
            disc(top, unit(sub(top, pivot)), 38, 8),
        ]
    )
    part(
        nm,
        arm,
        color=SILVER if k else "#212121",
        part_number=f"PD-15{k + 1}",
        properties={"material": "7075-T6"},
    )
for k, y in enumerate((-75, -25)):
    part(
        f"master_cylinder_{k + 1}",
        rod(S(110, y, FRAME_Z + 160), S(205, y, FRAME_Z + 160), 13),
        color=GOLD,
        part_number="PD-160",
    )
