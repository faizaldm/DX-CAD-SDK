# SPDX-License-Identifier: Apache-2.0
"""A two-level industrial steel platform, 3 x 2 bays.

An equipment platform in painted structural steel: UC 203x203x46 columns on
concrete plinths with base plates and four anchor bolts each, UB 356x171x51
main beams on bolted end plates, UB 254x146x31 secondary beams on fin plates,
CHS X-bracing with gusset plates in the end bays, angle knee braces, a
chequer-plate floor at level 1 and an open-grid galvanised grating at level 2,
a straight steel stair with grating treads, and side-mounted safety-yellow
handrails (top rail, knee rail, posts, toe boards) round every open edge.
Every section is a true I, channel or angle profile drawn with polygon_face
and swept along its member line, root radii included. Shows place() for
anchor bolts, floor panels and stair treads, mate() for the base plates,
part numbers by member mark (C1, B1, B2, ...) and section properties.

As it opens the platform is drawn light, so it builds in a few seconds: the
handrail tubes are six-sided (RAIL_SIDES = 0 draws them round), the end
plates and fin plates carry no bolts (BOLTS = True draws them), the chequer
pattern and the grating are sparse (LUG_PITCH = 240 and BAR_PITCH = 62 draw
them closer) and each member's faces are whole (MESH_SEG = 300 cuts them into
short facets). All five together build the full model, in about 25 s.

Tags: solid, assembly, mates, showcase
"""

# ---------------------------------------------------------------- grid and levels (mm)
BAY_X = 5000.0  # bay length along X
BAYS_X = 3
BAY_Y = 4000.0  # bay width along Y
BAYS_Y = 2
LEVEL_1 = 3500.0  # top of steel, level 1 (from the slab)
LEVEL_2 = 7000.0  # top of steel, level 2
PLINTH_H = 300.0  # concrete plinth above the slab

# ---------------------------------------------------------------- sections (h, b, tw, tf, r)
COLUMN = ("UC 203x203x46", 203.2, 203.6, 7.2, 11.0, 10.2)
BEAM = ("UB 356x171x51", 355.0, 171.5, 7.4, 11.5, 10.2)
SECONDARY = ("UB 254x146x31", 251.4, 146.1, 6.0, 8.6, 7.6)
BRACE_D, BRACE_T = 88.9, 5.0  # CHS 88.9x5.0
KNEE_LEG, KNEE_T = 70.0, 7.0  # L 70x70x7
KNEE_REACH = 700.0
STRINGER = ("PFC 230x90x32", 230.0, 90.0, 7.5, 14.0)

# ---------------------------------------------------------------- plates and bolts
BASE_PLATE, BASE_T = 450.0, 25.0
ANCHOR_D, ANCHOR_PITCH = 24.0, 330.0
END_PLATE_T = 15.0
BOLT_D = 20.0
FIN_T = 10.0
BOLTS = (
    False  # True draws the six M20 on every end plate and the three on every fin plate, 2 s slower
)

# ---------------------------------------------------------------- floors, stair, handrails
CHEQUER_T = 6.0
GRATING_T = 30.0
BAR_PITCH = 100.0  # grating bearing bars, centres: 62 draws half as many again, a second slower
LUG_PITCH = 600.0  # chequer plate pattern: 240 draws six times the lugs, a second slower
STAIR_W = 1000.0
STAIR_GOING = 250.0
MAX_RISE = 190.0
RAIL_H = 1100.0
KNEE_RAIL_H = 550.0
RAIL_D = 48.3
RAIL_OFFSET = 130.0  # handrail line outside the grid (side-mounted posts)
RAIL_SIDES = (
    6  # handrail tubes are drawn as prisms of this many sides; 0 draws them round, 12 s slower
)
POST_SPACING = 1700.0

PAINT = "#D35400"  # primary steel, painted orange
YELLOW = "#F2C200"
# galvanised items (anchors, floor panels, treads) go in with place() and keep the
# viewer's plain grey, which reads as hot-dip galvanising
CONCRETE = "#C4BFB5"
GRADE = "S355J2"

XS = [i * BAY_X for i in range(BAYS_X + 1)]
YS = [j * BAY_Y for j in range(BAYS_Y + 1)]
LEVELS = [LEVEL_1, LEVEL_2]
LX, LY = XS[-1], YS[-1]
COL_H, COL_B, COL_TW = COLUMN[1], COLUMN[2], COLUMN[3]
BM_H, BM_B, BM_TW = BEAM[1], BEAM[2], BEAM[3]
SC_H, SC_B, SC_TW = SECONDARY[1], SECONDARY[2], SECONDARY[3]
FLOOR_T = [CHEQUER_T, GRATING_T]
COL_Z0 = PLINTH_H + BASE_T
PANEL_X = BAY_X / 2  # floor panels span from a main beam to the mid-bay B3
MESH_SEG = (
    10000.0  # long members are built from facets this long (see line_path): 300 meshes them evenly
)


# ---------------------------------------------------------------- helpers
def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vlen(a):
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def unit(a):
    n = vlen(a)
    return (a[0] / n, a[1] / n, a[2] / n)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def arc(cx, cy, r, a0, a1, n=4):
    """Points strictly inside the arc from a0 to a1 degrees (the ends are the caller's)."""
    return [
        (
            cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
            cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)),
        )
        for k in range(1, n)
    ]


def i_profile(h, b, tw, tf, r):
    """A rolled I-section, centred, x across the flanges and y up the web, root radii faceted."""
    hb, hh, hw = b / 2, h / 2, tw / 2
    pts = [(-hb, -hh), (hb, -hh), (hb, -hh + tf), (hw + r, -hh + tf)]
    pts += arc(hw + r, -hh + tf + r, r, -90, -180)
    pts += [(hw, -hh + tf + r), (hw, hh - tf - r)]
    pts += arc(hw + r, hh - tf - r, r, 180, 90)
    pts += [
        (hw + r, hh - tf),
        (hb, hh - tf),
        (hb, hh),
        (-hb, hh),
        (-hb, hh - tf),
        (-hw - r, hh - tf),
    ]
    pts += arc(-hw - r, hh - tf - r, r, 90, 0)
    pts += [(-hw, hh - tf - r), (-hw, -hh + tf + r)]
    pts += arc(-hw - r, -hh + tf + r, r, 0, -90)
    pts += [(-hw - r, -hh + tf), (-hb, -hh + tf)]
    return pts


def angle_profile(leg, t):
    """An equal angle with its heel at the origin, legs along +x and +y."""
    return (
        [(0, 0), (leg, 0), (leg, t), (t + 6, t)]
        + arc(t + 6, t + 6, 6, -90, -180)
        + [(t, t + 6), (t, leg), (0, leg)]
    )


def line_path(start, end):
    """A straight path from start to end, drawn as short collinear lines.

    Sweeping along it instead of extruding splits each long side of a member into
    MESH_SEG-long faces, so the viewport meshes a 5 m beam as neat short facets.
    """
    d = unit(vsub(end, start))
    side = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    length = vlen(vsub(end, start))
    n = max(1, int(math.ceil(length / MESH_SEG)))
    sk = Sketch(Plane(start, unit(cross(d, side)), d)).move_to((0, 0))
    for k in range(1, n + 1):
        sk = sk.line_to((length * k / n, 0))
    return sk.path()


def member(profile, start, end, up):
    """A prismatic member: `profile` drawn square to the line start -> end, its y along `up`."""
    d = unit(vsub(end, start))
    face = polygon_face(profile, Plane(start, d, cross(up, d)))
    return sweep(face, line_path(start, end))


def rod(p0, p1, r):
    """A round bar from p0 to p1."""
    d = vsub(p1, p0)
    length = vlen(d)
    d = unit(d)
    c = make_cylinder(r, length)
    axis = cross((0, 0, 1), d)
    if vlen(axis) > 1e-9:
        c = rotate(c, (0, 0, 0), unit(axis), math.degrees(math.acos(max(-1.0, min(1.0, d[2])))))
    elif d[2] < 0:
        c = rotate(c, (0, 0, 0), (1, 0, 0), 180)
    return translate(c, p0)


def rail_bar(p0, p1, r):
    """A handrail tube from p0 to p1: round, or with RAIL_SIDES a prism of that many sides, whose
    flat faces the kernel fuses where rails cross posts far quicker than it does round ones."""
    if not RAIL_SIDES:
        return rod(p0, p1, r)
    d = vsub(p1, p0)
    length = vlen(d)
    d = unit(d)
    side = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    pts = [
        (r * math.cos(2 * math.pi * k / RAIL_SIDES), r * math.sin(2 * math.pi * k / RAIL_SIDES))
        for k in range(RAIL_SIDES)
    ]
    return extrude(polygon_face(pts, Plane(p0, d, unit(cross(side, d)))), length, d)


def tube(p0, p1, d, t):
    """A circular hollow section from p0 to p1."""
    axis = unit(vsub(p1, p0))
    side = (0, 0, 1) if abs(axis[2]) < 0.9 else (1, 0, 0)
    ring = (
        Sketch(Plane(p0, axis, unit(cross(side, axis))))
        .circle((0, 0), d / 2)
        .circle((0, 0), d / 2 - t)
    )
    return sweep(ring.face(), line_path(p0, p1))


def hexagon(af, plane, height, direction):
    r = af / math.sqrt(3)
    pts = [
        (r * math.cos(math.radians(30 + 60 * k)), r * math.sin(math.radians(30 + 60 * k)))
        for k in range(6)
    ]
    return extrude(polygon_face(pts, plane), height, direction)


def bolt_stub(d=BOLT_D, grip=0.0):
    """Nut, washer and thread end of a bolt standing on +X from x = 0 (one solid)."""
    washer = rod((-0.5, 0, 0), (3.5, 0, 0), d * 0.95)
    nut = hexagon(d * 1.5, Plane((3.0, 0, 0), (1, 0, 0), (0, 1, 0)), d * 0.8, (1, 0, 0))
    thread = rod((-0.5 - grip, 0, 0), (3 + d * 0.8 + 6, 0, 0), d / 2)
    return fuse_all([washer, nut, thread])


def comb(length, width, pitch, t, band, seg=2 * MESH_SEG):
    """Plan outline of a grating's bearing bars along x, banded at both ends.

    The bars are joined by end bands alternately at x = 0 and x = length, so the
    outline is one closed meander; extra points every `seg` along each bar keep
    the facets short.
    """
    n = int(round((width - t) / pitch)) + 1
    p = (width - t) / (n - 1)
    ys = [i * p for i in range(n)]
    pts = [(0, 0), (length, 0)]
    for i in range(n - 1):  # right side, going up
        if i % 2 == 0:  # slot open to the right, band at x = 0
            pts += [(length, ys[i] + t), (band, ys[i] + t), (band, ys[i + 1]), (length, ys[i + 1])]
    pts += [(length, width), (0, width)]
    for i in reversed(range(n - 1)):  # left side, going down
        if i % 2 == 1:  # slot open to the left, band at x = length
            pts += [
                (0, ys[i + 1]),
                (length - band, ys[i + 1]),
                (length - band, ys[i] + t),
                (0, ys[i] + t),
            ]
    out = []
    for k, a in enumerate(pts):
        b = pts[(k + 1) % len(pts)]
        m = max(1, int(math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / seg)))
        out += [(a[0] + (b[0] - a[0]) * q / m, a[1] + (b[1] - a[1]) * q / m) for q in range(m)]
    return out


def put(name, shape, at, turn=0.0):
    """A painted plate or fitting built once at the origin, turned about Z and moved to `at`."""
    if turn:
        shape = rotate(shape, (0, 0, 0), (0, 0, 1), turn)
    return part(name, translate(shape, at), color=PAINT)


def ident(name, mark, section, extra=None):
    props = {"material": GRADE, "section": section}
    if extra:
        props.update(extra)
    identity(name, part_number=mark, properties=props)


def grid(i, j):
    return f"{'ABCDEFGH'[i]}{j + 1}"


# -------------------------------------------------------------- slab, plinths, base plates, anchors
part(
    "ground_slab",
    make_box(LX + 7400, LY + 2400, 150, (-1500, -1200, -150)),
    color="#D9D5CC",
    part_number="SLAB-150",
    properties={"material": "C32/40 concrete"},
)

plinth = make_box(650, 650, PLINTH_H, (-325, -325, 0))
plinth = chamfer(plinth, 20, [e for e in edges_parallel_to(plinth, (0, 0, 1))])
bp_pts = [
    (-BASE_PLATE / 2 + 20, -BASE_PLATE / 2),
    (BASE_PLATE / 2 - 20, -BASE_PLATE / 2),
    (BASE_PLATE / 2, -BASE_PLATE / 2 + 20),
    (BASE_PLATE / 2, BASE_PLATE / 2 - 20),
    (BASE_PLATE / 2 - 20, BASE_PLATE / 2),
    (-BASE_PLATE / 2 + 20, BASE_PLATE / 2),
    (-BASE_PLATE / 2, BASE_PLATE / 2 - 20),
    (-BASE_PLATE / 2, -BASE_PLATE / 2 + 20),
]
base_plate = extrude(polygon_face(bp_pts), BASE_T)
a = ANCHOR_PITCH / 2
anchor_xy = [(-a, -a), (-a, a), (a, -a), (a, a)]
base_plate = hole(
    base_plate,
    outermost_face(base_plate, (0, 0, 1)),
    None,
    ANCHOR_D / 2 + 1.5,
    world=[(x, y, BASE_T) for x, y in anchor_xy],
)
anchor = rotate(bolt_stub(ANCHOR_D, grip=BASE_T + 60), (0, 0, 0), (0, 1, 0), -90)  # standing up +Z

for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        g = grid(i, j)
        part(
            f"plinth_{g}",
            translate(plinth, (x, y, 0)),
            color=CONCRETE,
            part_number="PL1",
            properties={"material": "C32/40 concrete", "size": "650 x 650 x 300"},
        )
        put(f"base_plate_{g}", base_plate, (x, y, PLINTH_H))
        ident(f"base_plate_{g}", "BP1", f"PL {BASE_PLATE:.0f}x{BASE_PLATE:.0f}x{BASE_T:.0f}")
        try:
            mate(f"base_plate_{g}", "<Z", f"plinth_{g}", ">Z", "coincident")
        except Exception:
            pass
        for k, (ax_, ay_) in enumerate(anchor_xy):
            name = f"anchor_{g}_{k + 1}"
            place(name, anchor, at=(x + ax_, y + ay_, PLINTH_H + BASE_T))
            identity(
                name,
                part_number="AB1",
                properties={
                    "material": "grade 8.8, galvanised",
                    "size": f"M{ANCHOR_D:.0f} cast-in anchor",
                },
            )

# ---------------------------------------------------------------- columns
col_profile = i_profile(*COLUMN[1:])
for i, x in enumerate(XS):
    for j, y in enumerate(YS):
        g = grid(i, j)
        col = member(col_profile, (x, y, COL_Z0), (x, y, LEVEL_2), (1, 0, 0))
        part(
            f"column_{g}",
            col,
            color=PAINT,
            part_number="C1",
            properties={
                "material": GRADE,
                "section": COLUMN[0],
                "length": f"{LEVEL_2 - COL_Z0:.0f} mm",
            },
        )


# --------------------------------------------------- end plates (built once, placed at every joint)
def end_plate(width, height, rows, gauge):
    plate = make_box(END_PLATE_T, width, height, (0, -width / 2, -height / 2))
    stub = translate(bolt_stub(), (END_PLATE_T, 0, 0))
    bolts = [translate(stub, (0, s * gauge / 2, z)) for z in rows for s in (-1, 1)]
    return fuse(plate, compound(bolts)) if BOLTS else plate


EP1 = end_plate(200.0, BM_H, (BM_H / 2 - 70, 0.0, -BM_H / 2 + 70), 100.0)
EP2 = end_plate(150.0, 250.0, (80.0, 0.0, -80.0), 90.0)

# fin plate: welded to the B1 web at y = 0, lapping the B3 web on its +X side, three bolts
FIN_REACH = BM_B / 2 + 10 - BM_TW / 2  # from the B1 web face to the end of B3
fin = make_box(FIN_T, FIN_REACH + 90, 180, (SC_TW / 2, 0, -210))
fin_bolts = []
for z in (-60.0, -120.0, -180.0):
    head = hexagon(
        BOLT_D * 1.5, Plane((-SC_TW / 2 - 13, 0, 0), (1, 0, 0), (0, 1, 0)), 13.5, (1, 0, 0)
    )
    b = fuse(head, translate(bolt_stub(grip=SC_TW + FIN_T + 2), (SC_TW / 2 + FIN_T, 0, 0)))
    fin_bolts.append(translate(b, (0, FIN_REACH + 45, z)))
FIN = fuse(fin, compound(fin_bolts)) if BOLTS else fin

# ---------------------------------------------------------------- beams
beam_profile = i_profile(*BEAM[1:])
sec_profile = i_profile(*SECONDARY[1:])
for lv, z in enumerate(LEVELS):
    L = f"L{lv + 1}"
    zc = z - BM_H / 2
    # B1: main beams along X, onto the column flanges
    for j, y in enumerate(YS):
        for i in range(BAYS_X):
            x0, x1 = XS[i] + COL_H / 2, XS[i + 1] - COL_H / 2
            name = f"B1_{L}_{grid(i, j)}-{grid(i + 1, j)}"
            beam = member(
                beam_profile, (x0 + END_PLATE_T, y, zc), (x1 - END_PLATE_T, y, zc), (0, 0, 1)
            )
            part(
                name,
                beam,
                color=PAINT,
                part_number="B1",
                properties={
                    "material": GRADE,
                    "section": BEAM[0],
                    "length": f"{x1 - x0 - 2 * END_PLATE_T:.0f} mm",
                },
            )
            put(f"{name}_EP_a", EP1, (x1, y, zc), 180)
            put(f"{name}_EP_b", EP1, (x0, y, zc))
            for s in ("a", "b"):
                ident(f"{name}_EP_{s}", "EP1", f"PL 200x{BM_H:.0f}x{END_PLATE_T:.0f}, 6 M20 8.8")
    # B2: main beams along Y, onto the column webs
    for i, x in enumerate(XS):
        for j in range(BAYS_Y):
            y0, y1 = YS[j] + COL_TW / 2, YS[j + 1] - COL_TW / 2
            name = f"B2_{L}_{grid(i, j)}-{grid(i, j + 1)}"
            beam = member(
                beam_profile, (x, y0 + END_PLATE_T, zc), (x, y1 - END_PLATE_T, zc), (0, 0, 1)
            )
            part(
                name,
                beam,
                color=PAINT,
                part_number="B2",
                properties={
                    "material": GRADE,
                    "section": BEAM[0],
                    "length": f"{y1 - y0 - 2 * END_PLATE_T:.0f} mm",
                },
            )
            put(f"{name}_EP_a", EP2, (x, y0, zc), 90)
            put(f"{name}_EP_b", EP2, (x, y1, zc), -90)
            for s in ("a", "b"):
                ident(f"{name}_EP_{s}", "EP2", f"PL 150x250x{END_PLATE_T:.0f}, 6 M20 8.8")
    # B3: secondary beams along Y at mid-bay, on fin plates off the B1 webs
    for i in range(BAYS_X):
        xc = XS[i] + BAY_X / 2
        for j in range(BAYS_Y):
            y0, y1 = YS[j] + BM_B / 2 + 10, YS[j + 1] - BM_B / 2 - 10
            name = f"B3_{L}_{grid(i, j)}"
            sec = member(sec_profile, (xc, y0, z - SC_H / 2), (xc, y1, z - SC_H / 2), (0, 0, 1))
            part(
                name,
                sec,
                color=PAINT,
                part_number="B3",
                properties={
                    "material": GRADE,
                    "section": SECONDARY[0],
                    "length": f"{y1 - y0:.0f} mm",
                },
            )
            put(f"{name}_FP_a", FIN, (xc, YS[j] + BM_TW / 2, z))
            put(f"{name}_FP_b", FIN, (xc, YS[j + 1] - BM_TW / 2, z), 180)
            for s in ("a", "b"):
                ident(f"{name}_FP_{s}", "FP1", f"PL 10x{FIN_REACH + 90:.0f}x180, 3 M20 8.8")


# --------------------------------------------------------------- vertical X-bracing in the end bays
def gusset(xf, zc, sx, sz, y):
    """A gusset in the plane y, its corner at (xf, zc), legs running sx along X and sz up Z."""
    pts = [
        (xf, zc),
        (xf + sx * 380, zc),
        (xf + sx * 380, zc + sz * 120),
        (xf + sx * 120, zc + sz * 380),
        (xf, zc + sz * 380),
    ]
    return extrude(polygon_face(pts, Plane((0, y - 6, 0), (0, -1, 0), (1, 0, 0))), 12, (0, 1, 0))


storeys = [(COL_Z0, LEVEL_1 - BM_H), (LEVEL_1, LEVEL_2 - BM_H)]
n_brace = 0
for j in (0, BAYS_Y):
    y = YS[j]
    for i in sorted({0, BAYS_X - 1}):
        xa, xb = XS[i] + COL_H / 2, XS[i + 1] - COL_H / 2
        for s, (zb, zt) in enumerate(storeys):
            corners = [(xa, zb, 1, 1), (xb, zt, -1, -1), (xa, zt, 1, -1), (xb, zb, -1, 1)]
            for k, (xf, zc, sx, sz) in enumerate(corners):
                gname = f"gusset_{grid(i, j)}-{grid(i + 1, j)}_S{s + 1}_{k + 1}"
                part(
                    gname,
                    gusset(xf, zc, sx, sz, y),
                    color=PAINT,
                    part_number="GP1",
                    properties={"material": GRADE, "section": "PL 12"},
                )
            for k in range(2):
                (x0, z0, sx0, sz0), (x1, z1, sx1, sz1) = corners[2 * k], corners[2 * k + 1]
                p0 = (x0 + sx0 * 170, y, z0 + sz0 * 170)
                p1 = (x1 + sx1 * 170, y, z1 + sz1 * 170)
                n_brace += 1
                part(
                    f"VB_{grid(i, j)}-{grid(i + 1, j)}_S{s + 1}_{k + 1}",
                    tube(p0, p1, BRACE_D, BRACE_T),
                    color=PAINT,
                    part_number="VB1",
                    properties={
                        "material": "S355J2H",
                        "section": f"CHS {BRACE_D}x{BRACE_T}",
                        "length": f"{vlen(vsub(p1, p0)):.0f} mm",
                    },
                )

# ---------------------------------------------------------------- knee braces on the inner frames
knee = angle_profile(KNEE_LEG, KNEE_T)
knee = [(px - KNEE_LEG / 2, py) for px, py in knee]
for lv, z in enumerate(LEVELS):
    for i in range(1, BAYS_X):
        x = XS[i]
        for j in range(BAYS_Y):
            for end, (yf, sy) in enumerate(((YS[j] + COL_TW / 2, 1), (YS[j + 1] - COL_TW / 2, -1))):
                p0 = (x, yf, z - BM_H - KNEE_REACH)
                p1 = (x, yf + sy * KNEE_REACH, z - BM_H)
                kb = member(knee, p0, p1, (1, 0, 0))
                part(
                    f"KB_L{lv + 1}_{grid(i, j)}_{end + 1}",
                    kb,
                    color=PAINT,
                    part_number="KB1",
                    properties={
                        "material": GRADE,
                        "section": f"L {KNEE_LEG:.0f}x{KNEE_LEG:.0f}x{KNEE_T:.0f}",
                    },
                )

# ---------------------------------------------------------------- level 1: chequer plate
lug = make_box(100, 20, 2.5, (-50, -10, CHEQUER_T - 0.5))


def chequer_panel(px, py, notch):
    plate = make_box(px, py, CHEQUER_T)
    plate = cut_all(
        plate,
        [
            make_box(notch + 1, notch + 1, CHEQUER_T + 2, (-1, -1, -1)),
            make_box(notch + 1, notch + 1, CHEQUER_T + 2, (-1, py - notch, -1)),
        ],
    )
    lugs = []
    pitch = LUG_PITCH
    for a_ in range(int(px // pitch)):
        for b_ in range(int(py // pitch)):
            cx, cy = pitch / 2 + a_ * pitch, pitch / 2 + b_ * pitch
            if cx < notch + 60 and (cy < notch + 60 or cy > py - notch - 60):
                continue
            one = translate(lug, (cx, cy, 0))
            if (a_ + b_) % 2:
                one = rotate(one, (cx, cy, 0), (0, 0, 1), 90)
            lugs.append(one)
    return fuse(plate, compound(lugs))


GAP = 5.0
NOTCH = COL_H / 2 + 12 - GAP
cp_left = chequer_panel(PANEL_X - 2 * GAP, BAY_Y - 2 * GAP, NOTCH)
cp_right = mirror(cp_left, ((PANEL_X - 2 * GAP) / 2, 0, 0), (1, 0, 0))
n_px = int(round(LX / PANEL_X))
for a_ in range(n_px):
    x0 = a_ * PANEL_X
    on_col = abs(x0 / BAY_X - round(x0 / BAY_X)) < 1e-6
    for j in range(BAYS_Y):
        name = f"chequer_L1_{a_ + 1}_{j + 1}"
        place(name, cp_left if on_col else cp_right, at=(x0 + GAP, YS[j] + GAP, LEVEL_1))
        identity(
            name,
            part_number="CP1",
            properties={
                "material": "S275 chequer plate, galvanised",
                "section": f"{CHEQUER_T:.0f} mm on {CHEQUER_T + 2:.0f} mm pattern",
            },
        )

# ---------------------------------------------------------------- level 2: open grating
gy = BAY_Y / 2 - 2 * GAP
gx = PANEL_X - 2 * GAP

# bearing bars 30 x 5, banded at both ends
grating = extrude(polygon_face(comb(gx, gy, BAR_PITCH, 5.0, 10.0)), GRATING_T)
for a_ in range(n_px):
    for b_ in range(2 * BAYS_Y):
        name = f"grating_L2_{a_ + 1}_{b_ + 1}"
        place(name, grating, at=(a_ * PANEL_X + GAP, b_ * BAY_Y / 2 + GAP, LEVEL_2))
        identity(
            name,
            part_number="GR1",
            properties={
                "material": "S275, hot-dip galvanised",
                "section": f"30 x 5 bearing bars at {BAR_PITCH:.0f} mm, banded",
            },
        )

# ---------------------------------------------------------------- stair to level 1
FL1 = LEVEL_1 + CHEQUER_T
N_RISE = int(math.ceil(FL1 / MAX_RISE))
RISE = FL1 / N_RISE
STAIR_Y = YS[0] + BAY_Y / 2
X_TOP = -BM_B / 2 - 5
slope = math.atan2(RISE, STAIR_GOING)
c_, s_ = math.cos(slope), math.sin(slope)
d_ = (c_, 0, s_)
up_ = (-s_, 0, c_)


def flip(shape):
    """The stair is drawn climbing +X to the grid line x = 0, then mirrored to the x = LX end."""
    return mirror(shape, (LX / 2, 0, 0), (1, 0, 0))


def nosing_z(x):
    return FL1 - (X_TOP - x) * RISE / STAIR_GOING


_, s_h, s_b, s_tw, s_tf = STRINGER
x_start = X_TOP - (N_RISE + 2) * STAIR_GOING
for side, sgn in (("left", -1), ("right", 1)):
    top = 70 * c_
    bot = top - s_h
    pts = [
        (0, top),
        (sgn * s_b, top),
        (sgn * s_b, top - s_tf),
        (sgn * s_tw, top - s_tf),
        (sgn * s_tw, bot + s_tf),
        (sgn * s_b, bot + s_tf),
        (sgn * s_b, bot),
        (0, bot),
    ]
    origin = (x_start, STAIR_Y + sgn * STAIR_W / 2, nosing_z(x_start))
    length = (X_TOP + 400 - x_start) / c_
    st_end = (origin[0] + length * c_, origin[1], origin[2] + length * s_)
    st = sweep(polygon_face(pts, Plane(origin, d_, (0, 1, 0))), line_path(origin, st_end))
    st = cut_all(
        st,
        [
            make_box(20000, 2000, 5000, (-15000, -1000 + STAIR_Y, -5000 + 15)),
            make_box(2000, 2000, 10000, (X_TOP - 5, -1000 + STAIR_Y, -2000)),
        ],
    )
    part(
        f"stringer_{side}",
        flip(st),
        color=PAINT,
        part_number="ST1",
        properties={"material": GRADE, "section": STRINGER[0]},
    )
    xa = X_TOP - (FL1 - 15 + top / c_) * STAIR_GOING / RISE  # top edge meets the foot plate
    xb = X_TOP - (FL1 - 15 + bot / c_) * STAIR_GOING / RISE  # bottom edge meets it
    yb = STAIR_Y + sgn * (STAIR_W / 2 + s_b / 2)
    part(
        f"stringer_foot_{side}",
        flip(make_box(xb - xa + 100, 200, 15, (xa - 50, yb - 100, 0))),
        color=PAINT,
        part_number="SP1",
        properties={"material": GRADE, "section": "PL 15"},
    )
    y_in = STAIR_Y + sgn * STAIR_W / 2
    cleat = make_box(10, s_b, 200, (X_TOP - 5, min(y_in, y_in + sgn * s_b), LEVEL_1 - 230))
    part(
        f"stringer_cleat_{side}",
        flip(cleat),
        color=PAINT,
        part_number="SC1",
        properties={"material": GRADE, "section": "PL 12"},
    )

# treads: grating with a chequer nosing and end cleats, built once, placed per step
TW = STAIR_W - 4
TD = STAIR_GOING - 10
t_bars = extrude(
    polygon_face(comb(TW, TD, 30.0, 5.0, 10.0), Plane((TD, -TW / 2, -30), (0, 0, 1), (0, 1, 0))), 30
)
tread = fuse_all(
    [
        t_bars,
        make_box(35, TW, 35, (0, -TW / 2, -32)),
        make_box(TD, 10, 30, (0, TW / 2 - 10, -30)),
        make_box(TD - 20, 8, 70, (10, -TW / 2, -70)),
        make_box(TD - 20, 8, 70, (10, TW / 2 - 8, -70)),
    ]
)
tread = mirror(tread, (0, 0, 0), (1, 0, 0))  # the stair climbs towards -X
for k in range(1, N_RISE):
    xk = X_TOP - (N_RISE - k) * STAIR_GOING + 5
    name = f"tread_{k:02d}"
    place(name, tread, at=(LX - xk, STAIR_Y, k * RISE))
    identity(
        name,
        part_number="TR1",
        properties={
            "material": "S275, hot-dip galvanised",
            "section": f"{STAIR_W:.0f} x {STAIR_GOING:.0f} grating tread",
        },
    )
# ---------------------------------------------------------------- handrails
RR = RAIL_D / 2  # posts, CHS 48.3
RAIL_R = 42.4 / 2  # rails, CHS 42.4


def posts_between(s0, s1):
    n = max(1, int(math.ceil((s1 - s0) / POST_SPACING)))
    return [s0 + (s1 - s0) * k / n for k in range(n + 1)]


def rail_frame(r0, r1, posts, corners, along, fixed, web, z, fz):
    """Top and knee rails from r0 to r1 along one side, side-mounted posts at `posts`."""

    def at(s, h):
        return (s, fixed, h) if along == "x" else (fixed, s, h)

    top_z, knee_z, foot_z = fz + RAIL_H - RR, fz + KNEE_RAIL_H, z - BM_H + 60
    e = RR * 0.4
    posts_, feet = [], []
    for s in posts:
        posts_.append(rail_bar(at(s, foot_z), at(s, top_z), RR))
        if s in corners:  # corner post: a block welded to the corner column's flange tips
            px, py = at(s, 0)[:2]
            gx = XS[0] if px < XS[0] else XS[-1]
            gy = YS[0] if py < YS[0] else YS[-1]
            ex = gx + math.copysign(COL_H / 2 - 3, px - gx)
            ey = gy + math.copysign(COL_B / 2 - 3, py - gy)
            feet.append(
                make_box(
                    abs(px - ex), abs(py - ey), z - 25 - foot_z, (min(px, ex), min(py, ey), foot_z)
                )
            )
            continue
        lo, hi = min(fixed, web) - 1, max(fixed, web) + 1  # bracket plate to the beam web
        if along == "x":
            feet.append(make_box(12, hi - lo, z - 25 - foot_z, (s - 6, lo, foot_z)))
        else:
            feet.append(make_box(hi - lo, 12, z - 25 - foot_z, (lo, s - 6, foot_z)))
    # one boolean per frame: the two rails and the brackets never touch one another, nor do
    # the posts, so all the posts go onto the rails and the brackets at once
    rails = [
        rail_bar(at(r0 - e, top_z), at(r1 + e, top_z), RAIL_R),
        rail_bar(at(r0 - e, knee_z), at(r1 + e, knee_z), RAIL_R),
    ]
    return fuse(compound(rails + feet), compound(posts_))


STAIR_GAP = STAIR_W / 2 + STRINGER[2] / 2 + 70
for lv, z in enumerate(LEVELS):
    fz = z + FLOOR_T[lv]
    L = f"L{lv + 1}"
    # (along, rail line, grid positions along it, outward sign, grid edge)
    sides = [
        ("x", -RAIL_OFFSET, XS, -1, YS[0]),
        ("x", LY + RAIL_OFFSET, XS, 1, YS[-1]),
        ("y", -RAIL_OFFSET, YS, -1, XS[0]),
        ("y", LX + RAIL_OFFSET, YS, 1, XS[-1]),
    ]
    for along, fixed, gpos, sgn, edge in sides:
        web = edge + sgn * BM_TW / 2
        tip = edge + sgn * BM_B / 2
        half_col = COL_H / 2 if along == "x" else COL_B / 2
        tag = f"{along}{'+' if sgn > 0 else '-'}"
        last = len(gpos) - 2
        for b in range(last + 1):
            first_end = gpos[0] - RAIL_OFFSET if b == 0 else gpos[b] + 10
            last_end = gpos[-1] + RAIL_OFFSET if b == last else gpos[b + 1] - 10
            # pieces: (rail from, rail to, first post, last post, toe from, toe to)
            p0 = (
                first_end
                if (b == 0 and along == "x")
                else (first_end + RR + 60 if b == 0 else first_end + 140)
            )
            p1 = (
                last_end
                if (b == last and along == "x")
                else (last_end - RR - 60 if b == last else last_end - 140)
            )
            r0 = first_end if b == 0 else p0
            r1 = last_end if b == last else p1
            t0, t1 = gpos[b] - BM_B / 2 - 6, gpos[b + 1] + BM_B / 2 + 6
            if b > 0:
                t0 = gpos[b] + 10
            if b < last:
                t1 = gpos[b + 1] - 10
            if lv == 0:
                t0, t1 = gpos[b] + half_col + 3, gpos[b + 1] - half_col - 3
            pieces_ = [(r0, r1, p0, p1, t0, t1)]
            if lv == 0 and along == "y" and sgn > 0 and b == 0:
                pieces_ = [
                    (r0, STAIR_Y - STAIR_GAP, p0, STAIR_Y - STAIR_GAP, t0, STAIR_Y - STAIR_GAP),
                    (STAIR_Y + STAIR_GAP, r1, STAIR_Y + STAIR_GAP, p1, STAIR_Y + STAIR_GAP, t1),
                ]
            for q, (a0, a1, q0, q1, u0, u1) in enumerate(pieces_):
                posts = posts_between(q0, q1)
                corners = [
                    s
                    for s in posts
                    if along == "x" and (s == gpos[0] - RAIL_OFFSET or s == gpos[-1] + RAIL_OFFSET)
                ]
                frame = rail_frame(a0, a1, posts, corners, along, fixed, web, z, fz)
                name = f"handrail_{L}_{tag}_{b + 1}{'ab'[q]}"
                part(
                    name,
                    frame,
                    color=YELLOW,
                    part_number="HR1",
                    properties={
                        "material": "S275, galvanised and painted",
                        "section": f"CHS {RAIL_D}x3.2",
                        "height": f"{RAIL_H:.0f} mm",
                    },
                )
                tb_y = tip if sgn > 0 else tip - 6
                if along == "x":
                    tb = make_box(u1 - u0, 6, fz + 100 - z, (u0, tb_y, z))
                else:
                    tb = make_box(6, u1 - u0, fz + 100 - z, (tb_y, u0, z))
                part(
                    f"toe_board_{L}_{tag}_{b + 1}{'ab'[q]}",
                    tb,
                    color=YELLOW,
                    part_number="TB1",
                    properties={"material": "S275, galvanised and painted", "section": "FL 100x6"},
                )

# stair handrails, one frame per side: posts on the stringer top flange, rails parallel to the pitch
for side, sgn in (("left", -1), ("right", 1)):
    y = STAIR_Y + sgn * (STAIR_W / 2 + s_b / 2)
    xb = X_TOP - (N_RISE - 1) * STAIR_GOING + 60
    xt = X_TOP - 2 * RR - 10
    post_x = posts_between(xb, X_TOP - STAIR_GOING)
    top0 = (xb, y, nosing_z(xb) + 1000)
    top1 = (xt, y, nosing_z(xt) + 1000)
    rails = [
        rail_bar(top0, top1, RAIL_R),
        rail_bar((xb, y, nosing_z(xb) + 500), (xt, y, nosing_z(xt) + 500), RAIL_R),
    ]
    posts = []
    for px in post_x:
        zt = nosing_z(px) + 70 + 0
        posts.append(rail_bar((px, y, zt - 30), (px, y, nosing_z(px) + 1000), RR))
    posts.append(rail_bar((xt, y, nosing_z(xt) + 1000 + RR), (xt, y, nosing_z(xt) + 500 - RR), RR))
    part(
        f"stair_handrail_{side}",
        flip(fuse(compound(rails), compound(posts))),
        color=YELLOW,
        part_number="HR2",
        properties={"material": "S275, galvanised and painted", "section": f"CHS {RAIL_D}x3.2"},
    )
