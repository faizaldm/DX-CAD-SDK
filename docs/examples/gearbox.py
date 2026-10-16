# SPDX-License-Identifier: Apache-2.0
"""A two-stage helical speed reducer, its cover cut away to show the gear train.

A machine-shop showcase: a painted cast-iron housing split at the shaft
centres, with ribs, feet, a bolted joint flange, eye bolts, an inspection
cover with breather, an oil sight glass and a drain plug. Inside, an input
pinion shaft, an intermediate shaft carrying a gear and a pinion, and an
output shaft with its large gear, all helical, each tooth an involute
outline lofted between two twisted sections, meshing at the true centre
distance m * (z1 + z2) / 2. Keys sit in keyways, the shafts run in ball and
taper roller bearings behind bolted caps with oil seals, and a flanged
coupling sits on the output shaft.

DX-CAD features shown: loft of involute outlines, revolved turned parts,
convex-hull cover profile extruded and shelled by booleans, circular
patterns of balls, rollers and bolts, place() for the eye bolts,
part numbers and properties on each part, and 3D text on the nameplate.
Change a module or a tooth count and the centre distances, housing, cover
and bearings follow; CUTAWAY = False closes the cover.

As it opens the teeth are drawn with straight flanks and the two big gears
with flat faces, so the model builds in a few seconds. FLANK = 4 draws each
involute and WEB = 0.34 recesses the big gears down to a web, for about four
times the build.

Tags: solid, assembly, text, showcase
"""

# ---------------------------------------------------------------- gearing
M1 = 3.0  # stage 1 normal module
Z1 = 18  # input pinion teeth
Z2 = 69  # stage 1 gear teeth
B1 = 40.0  # stage 1 face width
M2 = 4.0  # stage 2 normal module
Z3 = 19  # intermediate pinion teeth
Z4 = 73  # output gear teeth
B2 = 55.0  # stage 2 face width
HELIX = 12.0  # helix angle, degrees
PRESSURE = 20.0  # normal pressure angle, degrees
FLANK = (
    1  # straight pieces along each tooth flank: 4 draws the involute, and builds twice as slowly
)
WEB = 1.0  # the web of the two big gears, as a share of their face width: 0.34 recesses both faces

# -------------------------------------------------------------- bearings (bore, outside dia, width)
BRG_IN = (25.0, 52.0, 15.0)  # 6205
BRG_MID = (35.0, 72.0, 17.0)  # 6207
BRG_OUT = (55.0, 90.0, 23.0)  # 32011 taper roller

# ---------------------------------------------------------------- housing
WALL = 12.0  # cast wall
CLEAR = 10.0  # gear tip to wall
INNER = 80.0  # half the inside width (shafts run along Y)
BOSS_OUT = 20.0  # bearing bosses stand this far out of the walls
FLANGE_T = 16.0  # each half of the split flange
FLANGE_W = 28.0  # flange beyond the walls
BASE_T = 28.0  # base and feet
FOOT_W = 42.0  # feet beyond the walls
SUMP = 45.0  # oil below the output gear
CAP_T = 10.0  # bearing cap flange
INPUT_EXT = 50.0  # input shaft extension
OUTPUT_EXT = 65.0  # output shaft extension, into the coupling
CUTAWAY = True
TURN = -90.0  # the whole reducer is turned about Z so its cut-away faces the viewer
CUT_Y = 0.0  # the cover is cut away in front of this plane

# ---------------------------------------------------------------- colours
PAINT = "#2F5D8A"
MACHINED = "#C3C9D0"
SHAFT = "#D9DDE2"
STAGE1 = "#8C959E"
STAGE2 = "#C08A3A"
BEARING = "#B7BEC6"
BALL = "#ECEFF2"
ROLLER = "#9AA2AB"
BOLT = "#2E3238"
SEAL = "#1D1D1F"
BRASS = "#C9A23A"
GLASS = "#8FD3F0"
COUPLING = "#B23A2E"
KEY = "#757D86"

# ---------------------------------------------------------------- derived layout
BETA = math.radians(HELIX)


def transverse(mn):
    return mn / math.cos(BETA)


def pitch_r(mn, z):
    return transverse(mn) * z / 2


def tip_r(mn, z):
    return pitch_r(mn, z) + mn


A1 = transverse(M1) * (Z1 + Z2) / 2  # centre distances
A2 = transverse(M2) * (Z3 + Z4) / 2
X0, X1, X2 = 0.0, A1, A1 + A2  # shaft positions along X
RATIO = (Z2 / Z1) * (Z4 / Z3)

ZC = BASE_T + tip_r(M2, Z4) + SUMP  # shaft centres = joint plane
OUTER = INNER + WALL
BOSS_Y = OUTER + BOSS_OUT
SEAT = INNER + 4  # inner face of each bearing
Y_S1 = (15.0, 15.0 + B1)  # stage 1 plane (front)
Y_S2 = (-15.0 - B2, -15.0)  # stage 2 plane (back)

R_IN = [tip_r(M1, Z1) + CLEAR, tip_r(M1, Z2) + CLEAR, tip_r(M2, Z4) + CLEAR]
R_IN[0] = max(R_IN[0], BRG_IN[1] / 2 + 6)
XLI, XRI = X0 - R_IN[0] - 4, X2 + R_IN[2]
XLO, XRO = XLI - WALL, XRI + WALL
SHAFTS = [(X0, BRG_IN), (X1, BRG_MID), (X2, BRG_OUT)]


def boss_r(brg):
    return brg[1] / 2 + 18


def body_r(brg):
    return brg[0] / 2 + 3


# ---------------------------------------------------------------- helpers
def y_cyl(r, y0, y1, x, z=None):
    """A cylinder along +Y from y0 to y1 on the axis (x, z)."""
    z = ZC if z is None else z
    return translate(rotate(make_cylinder(r, y1 - y0), (0, 0, 0), (1, 0, 0), -90), (x, y0, z))


def z_cyl(r, z0, z1, x, y):
    return make_cylinder(r, z1 - z0, (x, y, z0))


def turned(profile, x, z=None):
    """A turned part: (radius, y) profile revolved about the shaft axis at (x, z)."""
    z = ZC if z is None else z
    face = polygon_face(profile, Plane((x, 0, z), (0, 0, 1), (1, 0, 0)))
    return revolve(face, (x, 0, z), (0, 1, 0))


def ring(ro, ri, y0, y1, x, z=None):
    return turned([(ri, y0), (ro, y0), (ro, y1), (ri, y1)], x, z)


def xz_prism(points, y0, y1):
    """A prism of an (x, z) outline, from y0 to y1."""
    return extrude(
        polygon_face(points, Plane((0, y0, 0), (0, -1, 0), (1, 0, 0))), y1 - y0, (0, 1, 0)
    )


def yz_prism(points, x0, x1):
    """A prism of a (y, z) outline, from x0 to x1."""
    return extrude(
        polygon_face(points, Plane((x0, 0, 0), (1, 0, 0), (0, 1, 0))), x1 - x0, (1, 0, 0)
    )


def mirror_y(shape):
    return mirror(shape, (0, 0, 0), (0, 1, 0))


def hull(points):
    """Convex hull, counter-clockwise (monotone chain)."""
    pts = sorted(set((round(x, 6), round(z, 6)) for x, z in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def hex_prism(af, h, z0=0.0):
    r = af / math.sqrt(3)
    pts = [
        (r * math.cos(math.radians(60 * k + 30)), r * math.sin(math.radians(60 * k + 30)))
        for k in range(6)
    ]
    return translate(extrude(polygon_face(pts), h), (0, 0, z0))


def hex_head(af, h, z0=0.0, both=False):
    """A hex head with its corners chamfered at 30 degrees, as a bolt or nut."""
    top = make_cone(0.48 * af + 1.73 * h, 0.48 * af, h, (0, 0, z0))
    head = common(hex_prism(af, h, z0), top)
    if both:
        head = common(head, make_cone(0.48 * af, 0.48 * af + 1.73 * h, h, (0, 0, z0)))
    return head


def bolt(d, length, af, head_h, washer=True):
    """A hex bolt standing on z = 0: shank down to -length, washer and head above."""
    pieces = [z_cyl(d / 2, -length, 0.5, 0, 0)]
    w = 0.0
    if washer:
        w = 0.18 * d
        pieces.append(z_cyl(1.0 * d, 0, w, 0, 0))
    pieces.append(hex_head(af, head_h, w - 0.2))
    return fuse_all(pieces)


def drill(shape, tools):
    """Cut tools that do not touch one another out of a shape in one cut, not a cut each."""
    return cut(shape, compound(tools))


def join(shape, pieces):
    """Fuse pieces that do not touch one another onto a shape in one fuse, as drill cuts."""
    return fuse(shape, compound(pieces)) if pieces else shape


def add(name, shape, **identity_):
    """Register a part, turned with the whole reducer by TURN about the vertical axis."""
    return part(name, rotate(shape, (0, 0, 0), (0, 0, 1), TURN), **identity_)


def turned_point(x, y, z):
    c, s = math.cos(math.radians(TURN)), math.sin(math.radians(TURN))
    return (x * c - y * s, x * s + y * c, z)


def fit(name, shape, at, turn=(0.0, 0.0, 0.0), color=BOLT, number=None, grade="8.8"):
    """A fastener turned about X, Y then Z and moved to `at`, as place() would, in its colour."""
    for axis, angle in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), turn, strict=True):
        if angle:
            shape = rotate(shape, (0, 0, 0), axis, angle)
    return add(
        name,
        translate(shape, at),
        color=color,
        part_number=number,
        properties={"material": f"steel, grade {grade}, black oxide"},
    )


def nut(d, af, h):
    return cut(hex_head(af, h, 0, both=True), z_cyl(d / 2, -1, h + 1, 0, 0))


# ---------------------------------------------------------------- involute gears
def outline(mn, z, turn):
    """A transverse gear outline: z involute teeth, tooth 0 centred on angle `turn` (radians)."""
    at = math.atan(math.tan(math.radians(PRESSURE)) / math.cos(BETA))
    r = pitch_r(mn, z)
    rb, ra, rf = r * math.cos(at), r + mn, r - 1.25 * mn

    def inv(a):
        return math.tan(a) - a

    half = math.pi / (2 * z) + inv(at) - 0.03 * mn / r  # half tooth angle less backlash

    def psi(p):
        return half - inv(math.acos(min(1.0, rb / p)))

    r0 = max(rb, rf)
    rad = [r0 + (ra - r0) * i / FLANK for i in range(FLANK + 1)]
    pts = []
    for k in range(z):
        c = 2 * math.pi * k / z + turn
        flank = [(p, c - psi(p)) for p in rad]
        if rf < rb:
            flank = [(rf, c - psi(rb))] + flank
        other = [(p, 2 * c - a) for p, a in reversed(flank)]
        nxt = c + 2 * math.pi / z - psi(r0)
        # at FLANK = 1 a tooth is its four corners; above it the tip and the root are rounded too
        tip = [(ra, c)] if FLANK > 1 else []
        land = (
            [(rf, c + psi(r0) + (nxt - c - psi(r0)) * t) for t in (0.33, 0.67)] if FLANK > 1 else []
        )
        for p, a in flank + tip + other + land:
            pts.append((p * math.cos(a), p * math.sin(a)))
    return pts


def helical(mn, z, y0, y1, ymid, hand, cx, turn):
    """A helical gear lofted between its two twisted end outlines; the teeth mesh at ymid."""
    r = pitch_r(mn, z)
    profiles = []
    for y in (y0, y1):
        twist = hand * (y - ymid) * math.tan(BETA) / r
        face = polygon_face(outline(mn, z, turn + twist), Plane((cx, y, ZC), (0, -1, 0), (1, 0, 0)))
        profiles.append(wires(face)[0])
    return loft(profiles)


def key_size(d):
    """(width, height, shaft depth) of a parallel key for a shaft of diameter d."""
    for top, size in (
        (22, (6, 6, 3.5)),
        (30, (8, 7, 4.0)),
        (38, (10, 8, 5.0)),
        (44, (12, 8, 5.0)),
        (58, (16, 10, 6.0)),
        (999, (18, 11, 7.0)),
    ):
        if d <= top:
            return size


def feather(r, y0, y1, x, swell=0.0):
    """A round-ended key (or its keyway with swell) on top of a shaft of radius r, from y0 to y1."""
    b, h, t1 = key_size(2 * r)
    b += swell
    z0 = ZC + r - t1
    z1 = z0 + h + swell
    pieces = [
        make_box(b, y1 - y0 - b, z1 - z0, (x - b / 2, y0 + b / 2, z0)),
        z_cyl(b / 2, z0, z1, x, y0 + b / 2),
        z_cyl(b / 2, z0, z1, x, y1 - b / 2),
    ]
    return fuse_all(pieces)


def keyway_in_hub(r, y0, y1, x):
    b, h, t1 = key_size(2 * r)
    return make_box(b + 0.2, y1 - y0 + 2, h - t1 + 1.5, (x - b / 2 - 0.1, y0 - 1, ZC + r - 1))


def webbed(gear, mn, z, y0, y1, x, bore):
    """Lighten a large gear: six holes and, with WEB under 1, both faces recessed to a web."""
    rim = pitch_r(mn, z) - 1.25 * mn - 2.5 * mn
    hub = bore * 1.85
    rh = (rim + hub) / 2
    holes = [
        y_cyl(
            0.28 * (rim - hub),
            y0 - 1,
            y1 + 1,
            x + rh * math.cos(math.radians(30 + 60 * k)),
            ZC + rh * math.sin(math.radians(30 + 60 * k)),
        )
        for k in range(6)
    ]
    bore_key = fuse(y_cyl(bore, y0 - 1, y1 + 1, x), keyway_in_hub(bore, y0, y1, x))
    if WEB >= 1:
        return drill(gear, holes + [bore_key])
    depth = (y1 - y0) * (1 - WEB) / 2
    pockets = fuse_all(
        [cut(y_cyl(rim, y0 - 1, y0 + depth, x), y_cyl(hub, y0 - 2, y0 + depth + 1, x))]
        + holes
        + [cut(y_cyl(rim, y1 - depth, y1 + 1, x), y_cyl(hub, y1 - depth - 1, y1 + 2, x))]
    )
    return drill(gear, [pockets, bore_key])  # one cut of the lofted teeth, far quicker than nine


# ---------------------------------------------------------------- cut-away
CUT_BOX = make_box(XRO - XLO + 600, 600, 800, (XLO - 300, CUT_Y, ZC))


def cutaway(shape, front=True):
    return cut(shape, CUT_BOX) if CUTAWAY and front else shape


def shown(x, y, z):
    """Whether a small part centred at (x, y, z) is left by the cut-away."""
    return not (CUTAWAY and y > CUT_Y and z > ZC)


# ---------------------------------------------------------------- housing: lower half
def bolt_circle(brg):
    n = 4 if brg[1] < 60 else 6
    rbc = brg[1] / 2 + 8.5
    start = 45 if n == 4 else 30
    return [(rbc, math.radians(start + k * 360 / n)) for k in range(n)]


FLANGE_BOLT_X = [XLO - 4, (X0 + X1) / 2, (X1 + X2) / 2, XRO + 4]
FLANGE_BOLT_Y = OUTER + FLANGE_W / 2 + 1
FOOT_HOLES = [
    (x, s * (OUTER + FOOT_W * 0.55)) for x in (XLO + 8, (X1 + X2) / 2, XRO - 8) for s in (-1, 1)
]
GLASS_AT = ((X1 + X2) / 2, BASE_T + (ZC - BASE_T - tip_r(M2, Z4)) + 38)
DRAIN_AT = (XRO - 30, BASE_T + 16)

halves_low = make_box(XRO - XLO + 400, 600, ZC + 1, (XLO - 200, -300, -1))
halves_up = make_box(XRO - XLO + 400, 600, 600, (XLO - 200, -300, ZC))

tapped = []
for xs, brg in SHAFTS:
    for rbc, a in bolt_circle(brg):
        for s in (-1, 1):
            y0 = BOSS_Y - 18 if s > 0 else -BOSS_Y - 1
            tapped.append(y_cyl(3.4, y0, y0 + 19, xs + rbc * math.cos(a), ZC + rbc * math.sin(a)))
bores = [y_cyl(brg[1] / 2, -BOSS_Y - 1, BOSS_Y + 1, xs) for xs, brg in SHAFTS]
flange_holes = [
    z_cyl(6.6, ZC - FLANGE_T - 1, ZC + FLANGE_T + 1, x, s * FLANGE_BOLT_Y)
    for x in FLANGE_BOLT_X
    for s in (-1, 1)
]

body = make_box(XRO - XLO, 2 * OUTER, ZC - BASE_T + 1, (XLO, -OUTER, BASE_T - 1))
body = fillet(body, 10, edges_parallel_to(body, (0, 0, 1)))
flange = make_box(
    XRO - XLO + 36, 2 * (OUTER + FLANGE_W), FLANGE_T, (XLO - 18, -OUTER - FLANGE_W, ZC - FLANGE_T)
)
flange = fillet(flange, 12, edges_parallel_to(flange, (0, 0, 1)))
plate = make_box(XRO - XLO + 24, 2 * (OUTER + FOOT_W), BASE_T - 8, (XLO - 12, -OUTER - FOOT_W, 8))
plate = fillet(plate, 14, edges_parallel_to(plate, (0, 0, 1)))
pads = [
    make_box(64, FOOT_W + 14, BASE_T, (x - 32, (OUTER - 6) if y > 0 else -(OUTER + FOOT_W + 8), 0))
    for x, y in FOOT_HOLES
]
bosses, ribs = [], []
for xs, brg in SHAFTS:
    br = boss_r(brg)
    bosses.append(common(y_cyl(br, -BOSS_Y, BOSS_Y, xs), halves_low))
    for s in (-1, 1):
        prof = [
            (OUTER - 1, BASE_T - 1),
            (OUTER + FOOT_W - 6, BASE_T - 1),
            (BOSS_Y - 2, ZC - 0.8 * br),
            (OUTER - 1, ZC - 0.8 * br),
        ]
        if s < 0:
            prof = [(-y, z) for y, z in reversed(prof)]
        ribs.append(yz_prism(prof, xs - 6, xs + 6))
spigots = [
    y_cyl(r, OUTER - 1, OUTER + 7, x, z)
    for x, z, r in ((GLASS_AT[0], GLASS_AT[1], 27.0), (DRAIN_AT[0], DRAIN_AT[1], 15.0))
]
# each group's pieces stand clear of one another, so a group goes on in one fuse
lower = fuse_all([body, flange, plate])
for group in (pads, bosses, ribs, spigots):
    lower = join(lower, group)
lower = cut(lower, make_box(XRI - XLI, 2 * INNER, ZC, (XLI, -INNER, BASE_T)))
lower = drill(
    lower,
    bores
    + [
        y_cyl(17, OUTER - 14, OUTER + 8, GLASS_AT[0], GLASS_AT[1]),
        y_cyl(7, OUTER - 14, OUTER + 8, DRAIN_AT[0], DRAIN_AT[1]),
    ],
)
lower = drill(
    lower, tapped + flange_holes + [z_cyl(9, -1, BASE_T + 1, x, y) for x, y in FOOT_HOLES]
)
add(
    "housing_lower",
    lower,
    color=PAINT,
    part_number="GR2-101",
    properties={"material": "EN-GJL-250 grey cast iron", "finish": "RAL 5014 enamel over primer"},
)


# ---------------------------------------------------------------- housing: cover (upper half)
def cover_profile(radii, xl, xr, zb):
    pts = [(xl, zb), (xr, zb)]
    for (xs, _), r in zip(SHAFTS, radii, strict=True):
        pts += [
            (xs + r * math.cos(math.radians(a)), ZC + r * math.sin(math.radians(a)))
            for a in range(0, 181, 6)
        ]
    return hull(pts)


R_OUT = [r + WALL for r in R_IN]
OUT_HULL = cover_profile(R_OUT, XLO, XRO, ZC)


def roof_z(x):
    best = ZC
    for (xa, za), (xb, zb) in zip(OUT_HULL, OUT_HULL[1:] + OUT_HULL[:1], strict=True):
        if min(xa, xb) <= x <= max(xa, xb) and xa != xb:
            best = max(best, za + (zb - za) * (x - xa) / (xb - xa))
    return best


# the inspection opening sits on the long straight run of roof between the two big gears
edges_up = [
    (p, q)
    for p, q in zip(OUT_HULL, OUT_HULL[1:] + OUT_HULL[:1], strict=True)
    if X1 < (p[0] + q[0]) / 2 < X2 and min(p[1], q[1]) > ZC + 20
]
(PA, PB) = max(edges_up, key=lambda e: math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))
INSP_SLOPE = math.degrees(math.atan2(PB[1] - PA[1], PB[0] - PA[0]))
INSP_AT = ((PA[0] + PB[0]) / 2, -INNER / 2 - 6, (PA[1] + PB[1]) / 2)
INSP_LEN = min(110.0, 0.8 * math.hypot(PB[0] - PA[0], PB[1] - PA[1]))
INSP_W = 66.0
EYES = [(X1, -INNER / 2 - 6), (X2 + 0.35 * R_OUT[2], -INNER / 2 - 6)]


def on_roof(shape):
    """Lay a shape built on the XY plane onto the inspection face of the roof."""
    return translate(rotate(shape, (0, 0, 0), (0, 1, 0), -INSP_SLOPE), INSP_AT)


top_flange = make_box(
    XRO - XLO + 36, 2 * (OUTER + FLANGE_W), FLANGE_T, (XLO - 18, -OUTER - FLANGE_W, ZC)
)
top_flange = fillet(top_flange, 12, edges_parallel_to(top_flange, (0, 0, 1)))
bosses, ribs = [], []
for xs, brg in SHAFTS:
    br = boss_r(brg)
    bosses.append(common(y_cyl(br, -BOSS_Y, BOSS_Y, xs), halves_up))
    top = roof_z(xs) - 6
    if top > ZC + br + 8:
        for s in (-1, 1):
            prof = [(OUTER - 1, ZC + 0.8 * br), (BOSS_Y - 2, ZC + 0.8 * br), (OUTER - 1, top)]
            if s < 0:
                prof = [(-y, z) for y, z in reversed(prof)]
            ribs.append(yz_prism(prof, xs - 6, xs + 6))
frame = on_roof(make_box(INSP_LEN + 16, INSP_W + 16, 10, (-INSP_LEN / 2 - 8, -INSP_W / 2 - 8, -6)))
eye_bosses = [z_cyl(19, roof_z(x) - 10, roof_z(x) + 4, x, y) for x, y in EYES]
cover = fuse(xz_prism(OUT_HULL, -OUTER, OUTER), top_flange)
for group in (bosses, ribs, [frame], eye_bosses):
    cover = join(cover, group)
inner_hull = cover_profile(R_IN, XLI, XRI, ZC - 1)
cover = cut(cover, xz_prism(inner_hull, -INNER, INNER))
cover = drill(
    cover,
    bores
    + [
        on_roof(
            make_box(INSP_LEN - 24, INSP_W - 24, 40, (-INSP_LEN / 2 + 12, -INSP_W / 2 + 12, -30))
        )
    ],
)
cover = drill(cover, [z_cyl(8.2, roof_z(x) - 20, roof_z(x) + 5, x, y) for x, y in EYES])
cover = drill(cover, tapped + flange_holes)
cover = cutaway(cover)
add(
    "housing_cover",
    cover,
    color=PAINT,
    part_number="GR2-102",
    properties={"material": "EN-GJL-250 grey cast iron", "finish": "RAL 5014 enamel over primer"},
)


# ---------------------------------------------------------------- shafts and gears
def shaft(xs, brg, ext):
    """A stepped shaft: journals in the bearings, a body between, an extension out of the front."""
    rj, rb = brg[0] / 2, body_r(brg)
    yb = -(SEAT + brg[2])
    prof = [(0, yb), (rj - 1, yb), (rj, yb + 1), (rj, -SEAT), (rb, -SEAT), (rb, SEAT), (rj, SEAT)]
    if ext:
        re = rj - 2.5
        y_ext = BOSS_Y + CAP_T + 2
        prof += [
            (rj, y_ext),
            (re, y_ext),
            (re, y_ext + ext - 1.5),
            (re - 1.5, y_ext + ext),
            (0, y_ext + ext),
        ]
    else:
        yf = SEAT + brg[2]
        prof += [(rj, yf - 1), (rj - 1, yf), (0, yf)]
    return turned(prof, xs)


ymid1 = sum(Y_S1) / 2
ymid2 = sum(Y_S2) / 2

# input pinion shaft: pinion cut integral with its shaft
x, brg = SHAFTS[0]
pinion1 = helical(M1, Z1, Y_S1[0] - 2, Y_S1[1] + 2, ymid1, 1, x, 0.0)
in_shaft = shaft(x, brg, INPUT_EXT)
re_in = brg[0] / 2 - 2.5
in_key_y = (BOSS_Y + CAP_T + 8, BOSS_Y + CAP_T + INPUT_EXT - 6)
in_shaft = cut(fuse(in_shaft, pinion1), feather(re_in, in_key_y[0], in_key_y[1], x, 0.1))
add(
    "input_pinion_shaft",
    in_shaft,
    color=STAGE1,
    part_number="GR2-201",
    properties={
        "material": "18CrNiMo7-6, case hardened",
        "teeth": str(Z1),
        "module": str(M1),
        "helix": f"{HELIX} RH",
    },
)
add(
    "input_key",
    feather(re_in, in_key_y[0], in_key_y[1], x),
    color=KEY,
    part_number="DIN6885-A6x6",
    properties={"material": "C45"},
)

# intermediate shaft with the stage 1 gear and the stage 2 pinion
x, brg = SHAFTS[1]
rb = body_r(brg)
mid_keys = [(Y_S1[0] + 4, Y_S1[1] - 4), (Y_S2[0] + 2, Y_S2[1] - 2)]
mid_shaft = drill(shaft(x, brg, 0), [feather(rb, a, b, x, 0.1) for a, b in mid_keys])
add(
    "intermediate_shaft",
    mid_shaft,
    color=SHAFT,
    part_number="GR2-301",
    properties={"material": "42CrMo4"},
)
gear2 = helical(M1, Z2, Y_S1[0], Y_S1[1], ymid1, -1, x, math.pi + math.pi / Z2)
gear2 = webbed(gear2, M1, Z2, Y_S1[0], Y_S1[1], x, rb)
add(
    "stage1_gear",
    gear2,
    color=STAGE1,
    part_number="GR2-302",
    properties={
        "material": "42CrMo4, induction hardened",
        "teeth": str(Z2),
        "module": str(M1),
        "centre distance": f"{A1:.2f}",
    },
)
pinion3 = helical(M2, Z3, Y_S2[0] - 2, Y_S2[1] + 2, ymid2, -1, x, 0.0)
pinion3 = cut(
    pinion3,
    fuse(y_cyl(rb, Y_S2[0] - 3, Y_S2[1] + 3, x), keyway_in_hub(rb, Y_S2[0] - 2, Y_S2[1] + 2, x)),
)
add(
    "stage2_pinion",
    pinion3,
    color=STAGE2,
    part_number="GR2-303",
    properties={"material": "18CrNiMo7-6, case hardened", "teeth": str(Z3), "module": str(M2)},
)
for k, (a, b) in enumerate(mid_keys):
    add(f"intermediate_key_{k + 1}", feather(rb, a, b, x), color=KEY, part_number="DIN6885-A12x8")

# output shaft with the big gear
x, brg = SHAFTS[2]
rb = body_r(brg)
re_out = brg[0] / 2 - 2.5
out_key = (Y_S2[0] + 4, Y_S2[1] - 4)
cpl_y = BOSS_Y + CAP_T + OUTPUT_EXT - 55
cpl_key = (cpl_y + 4, cpl_y + 40)
out_shaft = drill(
    shaft(x, brg, OUTPUT_EXT),
    [feather(rb, out_key[0], out_key[1], x, 0.1), feather(re_out, cpl_key[0], cpl_key[1], x, 0.1)],
)
add(
    "output_shaft",
    out_shaft,
    color=SHAFT,
    part_number="GR2-401",
    properties={"material": "42CrMo4"},
)
gear4 = helical(M2, Z4, Y_S2[0], Y_S2[1], ymid2, 1, x, math.pi + math.pi / Z4)
gear4 = webbed(gear4, M2, Z4, Y_S2[0], Y_S2[1], x, rb)
add(
    "output_gear",
    gear4,
    color=STAGE2,
    part_number="GR2-402",
    properties={
        "material": "42CrMo4, induction hardened",
        "teeth": str(Z4),
        "module": str(M2),
        "centre distance": f"{A2:.2f}",
        "ratio": f"{RATIO:.2f}",
    },
)
add("output_key", feather(rb, out_key[0], out_key[1], x), color=KEY, part_number="DIN6885-A18x11")
add(
    "coupling_key",
    feather(re_out, cpl_key[0], cpl_key[1], x),
    color=KEY,
    part_number="DIN6885-A14x9",
)

# spacer sleeves locating the gears against the bearings
SLEEVES = [
    (0, Y_S1[1] + 2, SEAT),
    (0, -SEAT, Y_S1[0] - 2),
    (1, Y_S1[1], SEAT),
    (1, Y_S2[1] + 2, Y_S1[0]),
    (1, -SEAT, Y_S2[0] - 2),
    (2, Y_S2[1], SEAT),
    (2, -SEAT, Y_S2[0]),
]
for k, (i, a, b) in enumerate(SLEEVES):
    xs, brg = SHAFTS[i]
    rb = body_r(brg)
    add(
        f"spacer_{k + 1}",
        ring(rb + 5, rb, a, b, xs),
        color=MACHINED,
        part_number=f"GR2-5{k + 1:02d}",
        properties={"material": "C45"},
    )


# ---------------------------------------------------------------- bearings
def ball_bearing(tag, xs, brg):
    d, D, w = brg
    rp = (d + D) / 4
    rball = (D - d) * 0.15
    y0, y1 = SEAT, SEAT + w
    yc = (y0 + y1) / 2
    groove = translate(
        rotate(make_torus(rp, rball * 1.03), (0, 0, 0), (1, 0, 0), -90), (xs, yc, ZC)
    )
    inner = cut(
        turned(
            [
                (d / 2, y0 + 0.6),
                (d / 2 + 0.6, y0),
                (rp - 0.55 * rball, y0),
                (rp - 0.55 * rball, y1),
                (d / 2 + 0.6, y1),
                (d / 2, y1 - 0.6),
            ],
            xs,
        ),
        groove,
    )
    outer = cut(
        turned(
            [
                (rp + 0.55 * rball, y0),
                (D / 2 - 0.6, y0),
                (D / 2, y0 + 0.6),
                (D / 2, y1 - 0.6),
                (D / 2 - 0.6, y1),
                (rp + 0.55 * rball, y1),
            ],
            xs,
        ),
        groove,
    )
    n = int(2 * math.pi * rp / (2.5 * rball))
    for side, sgn in (("front", 1), ("back", -1)):
        flip = (lambda s: s) if sgn > 0 else mirror_y
        add(
            f"{tag}_bearing_{side}_inner",
            cutaway(flip(inner), sgn > 0),
            color=BEARING,
            part_number=f"SKF 62{int(d / 5):02d}",
            properties={"type": "deep groove ball bearing", "bore": str(d)},
        )
        add(f"{tag}_bearing_{side}_outer", cutaway(flip(outer), sgn > 0), color=BEARING)
        for k in range(n):
            a = 2 * math.pi * (k + 0.5) / n
            bx, bz = xs + rp * math.cos(a), ZC + rp * math.sin(a)
            if sgn > 0 and CUTAWAY and bz - rball > ZC:
                continue
            ball = make_sphere(rball, (bx, sgn * yc, bz))
            if sgn > 0 and bz + rball > ZC:
                ball = cutaway(ball)
            add(f"{tag}_bearing_{side}_ball_{k + 1:02d}", ball, color=BALL)


def taper_bearing(tag, xs, brg):
    d, D, w = brg
    y0, y1 = SEAT, SEAT + w
    ri0, ri1 = d / 2 + 6.0, d / 2 + 7.5  # cone raceway, small end inboard
    ro0, ro1 = D / 2 - 5.5, D / 2 - 2.5  # cup raceway
    cone = turned(
        [
            (d / 2, y0 + 0.6),
            (d / 2 + 0.6, y0),
            (ri0 + 1.8, y0),
            (ri0 + 1.8, y0 + 2),
            (ri0, y0 + 2),
            (ri1, y1 - 3),
            (ri1 + 2.2, y1 - 3),
            (ri1 + 2.2, y1),
            (d / 2 + 0.6, y1),
            (d / 2, y1 - 0.6),
        ],
        xs,
    )
    cup = turned(
        [
            (ro0, y0 + 1),
            (D / 2 - 0.6, y0 + 1),
            (D / 2, y0 + 1.6),
            (D / 2, y1 - 0.6),
            (D / 2 - 0.6, y1),
            (ro1, y1),
        ],
        xs,
    )
    ya, yb_ = y0 + 2.5, y1 - 3.5

    def race(r0, r1, y):
        return r0 + (r1 - r0) * (y - y0) / (y1 - y0)

    ca = (race(ri0, ri1, ya) + race(ro0, ro1, ya)) / 2
    cb = (race(ri0, ri1, yb_) + race(ro0, ro1, yb_)) / 2
    rra = (race(ro0, ro1, ya) - race(ri0, ri1, ya)) / 2 - 0.1
    rrb = (race(ro0, ro1, yb_) - race(ri0, ri1, yb_)) / 2 - 0.1
    length = math.hypot(cb - ca, yb_ - ya)
    tilt = math.degrees(math.atan2(cb - ca, yb_ - ya))
    roller = rotate(
        rotate(make_cone(rra, rrb, length), (0, 0, 0), (1, 0, 0), -90), (0, 0, 0), (0, 0, 1), -tilt
    )
    n = int(2 * math.pi * (ca + cb) / 2 / (2.6 * max(rra, rrb)))
    for side, sgn in (("front", 1), ("back", -1)):
        flip = (lambda s: s) if sgn > 0 else mirror_y
        add(
            f"{tag}_bearing_{side}_cone",
            cutaway(flip(cone), sgn > 0),
            color=BEARING,
            part_number=f"SKF 320{int(d / 5):02d} X",
            properties={"type": "taper roller bearing", "bore": str(d)},
        )
        add(f"{tag}_bearing_{side}_cup", cutaway(flip(cup), sgn > 0), color=BEARING)
        for k in range(n):
            a = 360.0 * (k + 0.5) / n
            rz = ZC + ca * math.sin(math.radians(a))
            if sgn > 0 and not shown(0, 1, rz - rrb):
                continue
            r = rotate(translate(roller, (xs + ca, ya, ZC)), (xs, 0, ZC), (0, 1, 0), -a)
            r = flip(r)
            if sgn > 0 and rz + rrb + 3 > ZC:
                r = cutaway(r)
            add(f"{tag}_bearing_{side}_roller_{k + 1:02d}", r, color=ROLLER)


ball_bearing("input", *SHAFTS[0])
ball_bearing("intermediate", *SHAFTS[1])
taper_bearing("output", *SHAFTS[2])

# ---------------------------------------------------------------- bearing caps, seals, cap bolts
CAP_BOLT = bolt(8, 18, 13, 5.3)
for (xs, brg), tag, through in zip(
    SHAFTS, ("input", "intermediate", "output"), (True, False, True), strict=True
):
    d, D, w = brg
    rc = boss_r(brg) - 2
    yo = SEAT + w + 0.5
    rseal = d / 2 + 9
    for side, sgn in (("front", 1), ("back", -1)):
        open_cap = through and sgn > 0
        if open_cap:
            prof = [
                (d / 2 + 1, yo),
                (D / 2 - 0.3, yo),
                (D / 2 - 0.3, BOSS_Y),
                (rc, BOSS_Y),
                (rc, BOSS_Y + CAP_T - 1.5),
                (rc - 1.5, BOSS_Y + CAP_T),
                (rseal + 4, BOSS_Y + CAP_T),
                (rseal + 4, BOSS_Y + CAP_T + 4),
                (rseal, BOSS_Y + CAP_T + 4),
                (rseal, BOSS_Y + CAP_T - 6),
                (d / 2 + 1, BOSS_Y + CAP_T - 6),
            ]
        else:
            rf = D / 2 - 6
            prof = [
                (0, yo),
                (D / 2 - 0.3, yo),
                (D / 2 - 0.3, BOSS_Y),
                (rc, BOSS_Y),
                (rc, BOSS_Y + CAP_T - 1.5),
                (rc - 1.5, BOSS_Y + CAP_T),
                (rf, BOSS_Y + CAP_T),
                (rf, BOSS_Y + CAP_T + 3),
                (0, BOSS_Y + CAP_T + 3),
            ]
        cap = turned(prof, xs)
        holes = [
            y_cyl(4.5, BOSS_Y - 1, BOSS_Y + CAP_T + 1, xs + r * math.cos(a), ZC + r * math.sin(a))
            for r, a in bolt_circle(brg)
        ]
        cap = drill(cap, holes)
        if sgn < 0:
            cap = mirror_y(cap)
        add(
            f"{tag}_cap_{side}",
            cutaway(cap, sgn > 0),
            color=MACHINED,
            part_number=f"GR2-6{d:.0f}{'T' if open_cap else 'B'}",
            properties={
                "material": "EN-GJL-250",
                "type": "through cap with seal" if open_cap else "blind cap",
            },
        )
        if open_cap:
            seal = turned(
                [
                    (d / 2 - 0.3, BOSS_Y + CAP_T - 6),
                    (rseal + 0.2, BOSS_Y + CAP_T - 6),
                    (rseal + 0.2, BOSS_Y + CAP_T + 3),
                    (d / 2 + 3, BOSS_Y + CAP_T + 3),
                    (d / 2 + 3, BOSS_Y + CAP_T),
                    (d / 2 - 0.3, BOSS_Y + CAP_T - 2),
                ],
                xs,
            )
            add(
                f"{tag}_oil_seal",
                cutaway(seal),
                color=SEAL,
                part_number=f"DIN3760-A{d:.0f}x{2 * rseal:.0f}x8",
                properties={"material": "NBR"},
            )
        for k, (r, a) in enumerate(bolt_circle(brg)):
            bx, bz = xs + r * math.cos(a), ZC + r * math.sin(a)
            if sgn > 0 and not shown(bx, 1, bz):
                continue
            fit(
                f"{tag}_cap_{side}_bolt_{k + 1}",
                CAP_BOLT,
                (bx, sgn * (BOSS_Y + CAP_T), bz),
                (-90 * sgn, 0, 0),
                number="ISO4017-M8x20",
            )

# ---------------------------------------------------------------- joint flange bolts, foot bolts
JOINT_BOLT = bolt(12, 2 * FLANGE_T + 12, 18, 7.5)
JOINT_NUT = nut(12, 18, 10)
for i, x in enumerate(FLANGE_BOLT_X):
    for s, side in ((-1, "back"), (1, "front")):
        if not shown(x, s * FLANGE_BOLT_Y, ZC + 1):
            continue
        fit(
            f"joint_bolt_{side}_{i + 1}",
            JOINT_BOLT,
            (x, s * FLANGE_BOLT_Y, ZC + FLANGE_T),
            number="ISO4014-M12x45",
        )
        fit(
            f"joint_nut_{side}_{i + 1}",
            JOINT_NUT,
            (x, s * FLANGE_BOLT_Y, ZC - FLANGE_T - 10),
            number="ISO4032-M12",
        )
FOOT_BOLT = bolt(16, 40, 24, 10)
for k, (x, y) in enumerate(FOOT_HOLES):
    fit(f"foundation_bolt_{k + 1}", FOOT_BOLT, (x, y, BASE_T), number="ISO4014-M16x60")

# ------------------------------------------------------------ inspection cover, breather, eye bolts
insp = make_box(INSP_LEN, INSP_W, 5, (-INSP_LEN / 2, -INSP_W / 2, 4))
corners = [(sx * (INSP_LEN / 2 - 8), sy * (INSP_W / 2 - 8)) for sx in (-1, 1) for sy in (-1, 1)]
insp = drill(insp, [z_cyl(3.4, 0, 12, u, v) for u, v in corners] + [z_cyl(6, 0, 12, 0, 0)])
add(
    "inspection_cover",
    on_roof(insp),
    color=MACHINED,
    part_number="GR2-103",
    properties={"material": "S235"},
)
SCREW = bolt(6, 12, 10, 4, washer=False)
for k, (u, v) in enumerate(corners):
    fit(
        f"inspection_screw_{k + 1}",
        on_roof(translate(SCREW, (u, v, 9))),
        (0, 0, 0),
        number="ISO4017-M6x16",
    )
breather = fuse_all(
    [
        z_cyl(5.5, 2, 10, 0, 0),
        hex_head(22, 7, 9),
        z_cyl(5, 15.5, 24, 0, 0),
        make_cone(15, 9, 7, (0, 0, 23)),
        make_cone(9, 4, 3, (0, 0, 29.5)),
    ]
)
add(
    "breather",
    on_roof(breather),
    color=BRASS,
    part_number="GR2-BRT-M12",
    properties={"material": "CuZn39Pb3"},
)

EYE = fuse_all(
    [
        z_cyl(8, -16, 0.5, 0, 0),
        z_cyl(15, 0, 6, 0, 0),
        z_cyl(7.5, 5, 12, 0, 0),
        translate(rotate(make_torus(19, 5.5), (0, 0, 0), (1, 0, 0), 90), (0, 0, 33)),
    ]
)
for k, (x, y) in enumerate(EYES):
    place(f"eye_bolt_{k + 1}", EYE, at=turned_point(x, y, roof_z(x) + 4), rotate=(0, 0, TURN))
    identity(
        f"eye_bolt_{k + 1}",
        part_number="DIN580-M16",
        properties={"material": "C15E", "WLL": "700 kg"},
    )

# --------------------------------------------------------------- sight glass, drain plug, nameplate
gx, gz = GLASS_AT
add(
    "sight_glass_lens",
    y_cyl(17.5, OUTER + 3, OUTER + 9, gx, gz),
    color=GLASS,
    part_number="GR2-SG-30",
    properties={"material": "borosilicate"},
)
bezel = turned(
    [(15, OUTER + 7), (26, OUTER + 7), (26, OUTER + 11), (24.5, OUTER + 12.5), (15, OUTER + 12.5)],
    gx,
    gz,
)
bezel = drill(
    bezel,
    [
        y_cyl(
            2.2,
            OUTER,
            OUTER + 14,
            gx + 21 * math.cos(math.radians(a)),
            gz + 21 * math.sin(math.radians(a)),
        )
        for a in (45, 135, 225, 315)
    ],
)
add("sight_glass_bezel", bezel, color=MACHINED)
add(
    "sight_glass_level_mark",
    make_box(26, 0.8, 1.6, (gx - 13, OUTER + 8.6, gz - 0.8)),
    color="#D62728",
)
for k, a in enumerate((45, 135, 225, 315)):
    sx, sz = gx + 21 * math.cos(math.radians(a)), gz + 21 * math.sin(math.radians(a))
    add(
        f"sight_glass_screw_{k + 1}",
        fuse(
            y_cyl(1.9, OUTER + 2, OUTER + 13, sx, sz), y_cyl(3.6, OUTER + 12.4, OUTER + 15, sx, sz)
        ),
        color=BOLT,
    )
dx_, dz_ = DRAIN_AT
drain = fuse_all(
    [
        y_cyl(7, OUTER - 6, OUTER + 8, dx_, dz_),
        y_cyl(12, OUTER + 7, OUTER + 9, dx_, dz_),
        translate(rotate(hex_head(17, 8), (0, 0, 0), (1, 0, 0), -90), (dx_, OUTER + 8.5, dz_)),
    ]
)
add(
    "drain_plug",
    drain,
    color=BOLT,
    part_number="DIN910-M14x1.5",
    properties={"material": "5.8, magnetic"},
)

np_w = min(X1 - 30, 112.0)  # the nameplate sits in the bay under the input shaft
npx0, npx1 = X1 / 2 - np_w / 2, X1 / 2 + np_w / 2
npz0, npz1 = BASE_T + 30, BASE_T + 86
add(
    "nameplate",
    make_box(npx1 - npx0, 2, npz1 - npz0, (npx0, OUTER - 0.5, npz0)),
    color="#C9CDD2",
    part_number="GR2-NP",
)
txt_plane = Plane(((npx0 + npx1) / 2, OUTER + 1.2, 0), (0, 1, 0), (-1, 0, 0))
lettering = [
    text3d("DX-CAD R2H", 10, 0.8, plane=txt_plane, at=(0, npz1 - 18), align="centre"),
    text3d(
        f"i = {RATIO:.2f}  m {M1:g}/{M2:g}",
        7,
        0.8,
        plane=txt_plane,
        at=(0, npz0 + 9),
        align="centre",
    ),
]
# solids() hands a text's letters back in no fixed order: taken by place, so that each
# part keeps its letter from one run to the next
glyphs = [
    g
    for t in lettering
    for g in sorted(solids(t), key=lambda s: [round(v, 3) for v in bounding_box(s)[0]])
]
for k, g in enumerate(glyphs):
    add(f"nameplate_glyph_{k + 1:02d}", g, color="#1B2430")

# ---------------------------------------------------------------- output coupling
xo, brg = SHAFTS[2]
re = re_out
CPL_R = re + 44  # coupling flange radius
CPL_BC = re + 31  # its bolt circle
hub = turned(
    [
        (re, cpl_y),
        (re + 17, cpl_y),
        (re + 19, cpl_y + 2),
        (re + 19, cpl_y + 40),
        (CPL_R - 2, cpl_y + 40),
        (CPL_R, cpl_y + 42),
        (CPL_R, cpl_y + 56),
        (CPL_R - 2, cpl_y + 58),
        (re, cpl_y + 58),
    ],
    xo,
)
cpl_holes = [
    y_cyl(
        6.5,
        cpl_y + 30,
        cpl_y + 130,
        xo + CPL_BC * math.cos(math.radians(30 + 60 * k)),
        ZC + CPL_BC * math.sin(math.radians(30 + 60 * k)),
    )
    for k in range(6)
]
hub_a = drill(hub, cpl_holes + [keyway_in_hub(re, cpl_key[0], cpl_key[1], xo)])
add(
    "coupling_hub_drive",
    hub_a,
    color=COUPLING,
    part_number="GR2-CPL-50",
    properties={"material": "EN-GJS-400 ductile iron", "type": "rigid flange coupling"},
)
mirror_at = cpl_y + 58.5
hub_b = drill(mirror(hub, (0, mirror_at, 0), (0, 1, 0)), cpl_holes)
add("coupling_hub_driven", hub_b, color=COUPLING, part_number="GR2-CPL-50")
add(
    "driven_shaft",
    turned(
        [
            (0, mirror_at + 2),
            (re, mirror_at + 2),
            (re, mirror_at + 110),
            (re - 1.5, mirror_at + 111.5),
            (0, mirror_at + 111.5),
        ],
        xo,
    ),
    color=SHAFT,
    part_number="CUSTOMER",
)
CPL_BOLT = bolt(12, 42, 18, 7.5)
CPL_NUT = nut(12, 18, 10)
for k in range(6):
    a = math.radians(30 + 60 * k)
    bx, bz = xo + CPL_BC * math.cos(a), ZC + CPL_BC * math.sin(a)
    fit(
        f"coupling_bolt_{k + 1}",
        CPL_BOLT,
        (bx, cpl_y + 40, bz),
        (90, 0, 0),
        number="ISO4014-M12x50",
        grade="10.9",
    )
    fit(
        f"coupling_nut_{k + 1}",
        CPL_NUT,
        (bx, 2 * mirror_at - cpl_y - 40, bz),
        (-90, 0, 0),
        number="ISO4032-M12",
    )
