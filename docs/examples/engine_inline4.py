# SPDX-License-Identifier: Apache-2.0
"""Inline-four DOHC petrol engine, cut away.

A 1.8 litre inline-four as a machined-component showcase. The aluminium
block is sectioned through the bores on the intake side to show the water
jacket, the pistons with their ring grooves and gudgeon pins, the I-beam
connecting rods with bolted big-end caps and the crankshaft with its
counterweight webs, flywheel ring gear and front pulley. The pistons and
rods are placed from CRANK_ANGLE by the exact slider-crank relation, so
changing that one number turns the engine over. Above sit the cylinder head
with two camshafts, 16 inclined valves with springs, retainers and bucket
tappets, the cam bearing caps, sprockets and timing chain, the red cam cover
cut open over the front two cylinders, coil-on-plug ignition, swept intake
runners into a plenum with port injectors on a fuel rail, and a 4-into-1
heat-blued exhaust header.

DX-CAD features shown: revolved and extruded sketch profiles, swept paths,
booleans and shelling, circular and linear repetition, place() for every
moving and repeated part, mates confirming the pulley and flywheel on the
crankshaft, part numbers and material properties for the bill of materials.

As it opens each cam lobe is drawn with LOBE = 24 straight pieces, so the
model builds quickly; 64 draws the lobes smooth.

Tags: solid, assembly, mates, sketch, showcase
"""

BORE = 81.0  # cylinder bore
STROKE = 86.0  # crank throw x 2
ROD_LENGTH = 143.0  # big-end centre to small-end centre
BORE_PITCH = 91.0  # cylinder centre spacing along the crankshaft
COMP_HEIGHT = 31.0  # gudgeon pin centre to piston crown
CRANK_ANGLE = 40.0  # degrees after top dead centre of cylinder 1
MAIN_R = 26.0  # main journal radius
PIN_R = 22.0  # crankpin radius
VALVE_ANGLE = 20.0  # valve inclination from the bore axis, each side
HEAD_H = 100.0  # cylinder head height, deck to cam carrier
CUTAWAY = True  # section the block, head and cam cover
LOBE = 24  # straight pieces round each cam lobe: 64 draws it smooth, and builds a second slower

ALU = "#B8BCC2"
STEEL = "#6E7378"
PISTON_C = "#D9DCDF"
RED = "#B71C1C"
BLACK = "#1E1F21"
BLUED = "#5D6D7E"
DARK = "#4A4F55"
BRIGHT = "#A9AEB4"

# ------------------------------------------------------------------ derived layout
CR = STROKE / 2
XC = [(i - 1.5) * BORE_PITCH for i in range(4)]
PHASE = [0.0, 180.0, 180.0, 0.0]  # flat-plane crank, firing order 1-3-4-2
MAIN_LEN = 22.0
PIN_LEN = 24.0
WEB = (BORE_PITCH - PIN_LEN - MAIN_LEN) / 2
MAIN_X = [XC[0] - BORE_PITCH / 2 + k * BORE_PITCH for k in range(5)]
SKIRT = 26.0
CW_R = CR + 24
DECK_Z = ROD_LENGTH + CR + COMP_HEIGHT + 1.0
XB0 = MAIN_X[0] - MAIN_LEN / 2 - 14
XB1 = MAIN_X[4] + MAIN_LEN / 2 + 14
LINER_R = max(BORE / 2 + 5, BORE_PITCH / 2 + 1.5)
BW = LINER_R + 14
HW = BORE / 2 + 52
SKIRT_Z = -(CR + 20)
CUT_X = MAIN_X[0]
VX = BORE * 0.21  # valve offset either side of the bore centre, along X
V_OFF = 14.0  # valve axis offset from the bore centre at the deck
S_CAM = 129.0  # cam axis distance along the valve axis
SA, CA = math.sin(math.radians(VALVE_ANGLE)), math.cos(math.radians(VALVE_ANGLE))
YC = V_OFF + S_CAM * SA
ZC = DECK_Z + S_CAM * CA
FRONT = XB1


# ------------------------------------------------------------------ helpers
def x_cyl(r, length, x0, y=0.0, z=0.0):
    return translate(rotate(make_cylinder(r, length), (0, 0, 0), (0, 1, 0), 90), (x0, y, z))


def y_cyl(r, length, x, y0, z):
    return translate(rotate(make_cylinder(r, length), (0, 0, 0), (1, 0, 0), -90), (x, y0, z))


def drill(shape, tools):
    """Cut tools that do not touch one another out of a shape in one cut, not a cut each."""
    return cut(shape, compound(tools))


def join(shape, pieces):
    """Fuse pieces that do not touch one another onto a shape in one fuse."""
    return fuse(shape, compound(pieces))


def x_tube(r_out, r_in, length, x0, y=0.0, z=0.0):
    return cut(x_cyl(r_out, length, x0, y, z), x_cyl(r_in, length + 2, x0 - 1, y, z))


def yz_face(points, x):
    return polygon_face(points, Plane((x, 0, 0), (1, 0, 0), (0, 1, 0)))


def about_x(profile):
    """Revolve an (x, r) profile about the crank axis."""
    return revolve(
        polygon_face(profile, Plane((0, 0, 0), (0, -1, 0), (1, 0, 0))), (0, 0, 0), (1, 0, 0)
    )


def about_z(profile):
    """Revolve an (r, z) profile about the Z axis."""
    return revolve(
        polygon_face(profile, Plane((0, 0, 0), (0, -1, 0), (1, 0, 0))), (0, 0, 0), (0, 0, 1)
    )


def hex_prism(across_flats, h, x, y, z):
    rc = across_flats / math.sqrt(3)
    pts = [
        (x + rc * math.cos(math.radians(30 + 60 * k)), y + rc * math.sin(math.radians(30 + 60 * k)))
        for k in range(6)
    ]
    return extrude(polygon_face(pts, Plane.XY.offset(z)), h)


def bolt(x, y, z_head, r, length, af, head_h, down=False):
    """A hex-head bolt on a vertical axis; the head sits on z_head, the shank runs away from it."""
    if down:
        return fuse(
            hex_prism(af, head_h, x, y, z_head - head_h),
            make_cylinder(r, length, (x, y, z_head - 0.5)),
        )
    return fuse(
        hex_prism(af, head_h, x, y, z_head), make_cylinder(r, length, (x, y, z_head - length + 0.5))
    )


def gear_points(n, r_root, r_tip, cy=0.0, cz=0.0):
    pts = []
    step = 2 * math.pi / n
    for k in range(n):
        a = k * step
        for frac, r in ((-0.30, r_root), (-0.11, r_tip), (0.11, r_tip), (0.30, r_root)):
            pts.append((cy + r * math.cos(a + frac * step), cz + r * math.sin(a + frac * step)))
    return pts


def sprocket(n, r_root, r_tip, r_bore, x0, width, cy=0.0, cz=0.0, holes=0):
    body = extrude(yz_face(gear_points(n, r_root, r_tip, cy, cz), x0), width, (1, 0, 0))
    tools = [x_cyl(r_bore, width + 2, x0 - 1, cy, cz)]
    for k in range(holes):
        a = 2 * math.pi * k / holes
        rr = (r_root + r_bore) / 2
        tools.append(
            x_cyl(
                (r_root - r_bore) * 0.22,
                width + 2,
                x0 - 1,
                cy + rr * math.cos(a),
                cz + rr * math.sin(a),
            )
        )
    return drill(body, tools)


def hull(points):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in points))

    def turn(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and turn(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and turn(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def circle_pts(cy, cz, r, n=48):
    return [
        (cy + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n))
        for k in range(n)
    ]


def band(circles, x0, width, inner, outer):
    """A chain or belt: the hull round some (y, z, r) circles, from r + inner to r + outer."""
    out_pts = hull([p for cy, cz, r in circles for p in circle_pts(cy, cz, r + outer)])
    in_pts = hull([p for cy, cz, r in circles for p in circle_pts(cy, cz, r + inner)])
    body = extrude(yz_face(out_pts, x0), width, (1, 0, 0))
    hole = extrude(yz_face(in_pts, x0 - 1), width + 2, (1, 0, 0))
    return cut(body, hole)


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_unit(a):
    n = math.sqrt(v_dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def bend_end(p, t, d, radius):
    """Where a circular bend of `radius` leaving p along t ends once it heads along d."""
    c = max(-1.0, min(1.0, v_dot(t, d)))
    th = math.acos(c)
    n = v_unit(v_sub(d, v_mul(t, c)))
    return v_add(p, v_add(v_mul(t, radius * math.sin(th)), v_mul(n, radius * (1 - c))))


def line_edge(p, q):
    return BRepBuilderAPI_MakeEdge(gp_Pnt(*p), gp_Pnt(*q)).Edge()


def arc_edge(p, t, q):
    return BRepBuilderAPI_MakeEdge(
        GC_MakeArcOfCircle(gp_Pnt(*p), gp_Vec(*t), gp_Pnt(*q)).Value()
    ).Edge()


def pipe(path_edges, start, normal, r_out, r_in):
    """Sweep a tube section along a path that starts at `start` heading along `normal`."""
    x_dir = (1, 0, 0) if abs(normal[0]) < 0.9 else (0, 1, 0)
    plane = Plane(start, normal, x_dir)
    face = Sketch(plane).circle((0, 0), r_out).circle((0, 0), r_in).face()
    return sweep(face, make_wire(path_edges))


def put(name, shape, color, at=(0.0, 0.0, 0.0), tilt=0.0, part_number=None, properties=None):
    """Register a copy of `shape` turned `tilt` degrees about X and moved to `at`, in colour."""
    moved = translate(rotate(shape, (0, 0, 0), (1, 0, 0), tilt), at)
    return part(name, moved, color=color, part_number=part_number, properties=properties)


def slider_crank(theta):
    """Crankpin (y, z), gudgeon pin z and rod tilt for crank angle theta (degrees)."""
    t = math.radians(theta)
    yp, zp = -CR * math.sin(t), CR * math.cos(t)
    zpin = zp + math.sqrt(ROD_LENGTH**2 - yp**2)
    return yp, zp, zpin, math.degrees(math.asin(yp / ROD_LENGTH))


# ================================================================== crankshaft
def web(x0, phase):
    pts = [
        (0 + (PIN_R + 9) * math.cos(math.radians(a)), CR + (PIN_R + 9) * math.sin(math.radians(a)))
        for a in range(0, 181, 15)
    ]
    pts += [
        (CW_R * math.sin(math.radians(a)), -CW_R * math.cos(math.radians(a)))
        for a in range(-68, 69, 8)
    ]
    w = extrude(yz_face(pts, x0), WEB, (1, 0, 0))
    return rotate(w, (0, 0, 0), (1, 0, 0), phase)


mains = [x_cyl(MAIN_R, MAIN_LEN + 2, MAIN_X[0] - MAIN_LEN / 2 - 1)]
webs, pins = [], []
for i in range(4):
    xa = XC[i] - PIN_LEN / 2 - WEB
    webs.append(web(xa, PHASE[i]))
    pin = x_cyl(PIN_R, PIN_LEN + 2 * WEB - 4, xa + 2, 0, CR)
    pins.append(rotate(pin, (0, 0, 0), (1, 0, 0), PHASE[i]))
    webs.append(web(XC[i] + PIN_LEN / 2, PHASE[i]))
    mains.append(x_cyl(MAIN_R, MAIN_LEN + 4, MAIN_X[i + 1] - MAIN_LEN / 2 - 2))
mains[4] = fuse_all(
    [
        mains[4],
        x_cyl(MAIN_R - 2, FRONT + 4 - MAIN_X[4], MAIN_X[4]),  # timing journal
        x_cyl(20.0, 60, FRONT),
    ]
)  # snout
mains[0] = fuse_all(
    [
        mains[0],
        x_cyl(MAIN_R, MAIN_X[0] - MAIN_LEN / 2 - XB0 + 8, XB0 - 6),  # rear seal journal
        x_cyl(44.0, 10, XB0 - 16),
    ]
)  # flywheel flange
# the webs stand clear of one another, as do the journals and the pins: one fuse, not twenty
crank = fuse(compound(webs), compound(mains + pins))
oil_holes = [
    rotate(
        make_cylinder(3.5, 2 * PIN_R + 2, (XC[i], 0, CR - PIN_R - 1)), (XC[i], 0, CR), (1, 0, 0), 30
    )
    for i in range(4)
]
crank = drill(crank, [rotate(h, (0, 0, 0), (1, 0, 0), PHASE[i]) for i, h in enumerate(oil_holes)])
crank = rotate(crank, (0, 0, 0), (1, 0, 0), CRANK_ANGLE)
part(
    "crankshaft",
    crank,
    color=STEEL,
    part_number="ENG-110",
    properties={"material": "forged 42CrMo4, induction hardened"},
)

# flywheel, ring gear, crank sprocket, pulley
fw_x = XB0 - 16
flywheel = about_x(
    [
        (fw_x - 30, 20),
        (fw_x, 20),
        (fw_x, 60),
        (fw_x - 14, 70),
        (fw_x - 14, 120),
        (fw_x - 2, 128),
        (fw_x - 2, 140),
        (fw_x - 30, 140),
    ]
)
fw_tools = [
    x_cyl(5.5, 40, fw_x - 35, 34 * math.cos(math.radians(a)), 34 * math.sin(math.radians(a)))
    for a in range(0, 360, 60)
]
fw_tools += [
    x_cyl(13, 20, fw_x - 20, 95 * math.cos(math.radians(a)), 95 * math.sin(math.radians(a)))
    for a in range(30, 360, 60)
]
part(
    "flywheel",
    drill(flywheel, fw_tools),
    color=DARK,
    part_number="ENG-120",
    properties={"material": "nodular cast iron"},
)
ring = extrude(yz_face(gear_points(120, 150, 156), fw_x - 28), 14, (1, 0, 0))
part(
    "ring_gear",
    cut(ring, x_cyl(139, 20, fw_x - 30)),
    color=STEEL,
    part_number="ENG-121",
    properties={"material": "C45 induction hardened"},
)
part("crank_sprocket", sprocket(19, 22, 26, 20, FRONT + 2, 10), color=STEEL, part_number="ENG-131")
pul_x = FRONT + 24
pulley_prof = [(pul_x, 20), (pul_x + 30, 20), (pul_x + 30, 62)]
for k in range(6):
    xg = pul_x + 28 - k * 4.5
    pulley_prof += [(xg, 62), (xg - 2.25, 58.5)]
pulley_prof += [
    (pul_x + 2, 62),
    (pul_x, 62),
    (pul_x, 50),
    (pul_x + 10, 46),
    (pul_x + 10, 32),
    (pul_x, 30),
]
pulley = drill(
    about_x(pulley_prof),
    [
        x_cyl(7, 40, pul_x - 5, 38 * math.cos(math.radians(a)), 38 * math.sin(math.radians(a)))
        for a in range(45, 360, 90)
    ],
)
part(
    "crank_pulley",
    pulley,
    color=DARK,
    part_number="ENG-130",
    properties={"material": "cast iron, rubber damper"},
)

# ================================================================== pistons, pins, rods
R = BORE / 2 - 0.3
CH = COMP_HEIGHT
prof = [(0, CH), (R, CH)]
for top, bot in ((CH - 4.5, CH - 6.5), (CH - 9.0, CH - 11.0), (CH - 13.5, CH - 17.0)):
    prof += [(R, top), (R - 3, top), (R - 3, bot), (R, bot)]
prof += [
    (R, -SKIRT),
    (R - 4, -SKIRT),
    (R - 4, CH - 20),
    (R - 9, CH - 20),
    (R - 9, CH - 8),
    (0, CH - 8),
]
piston = about_z(prof)
boss = common(x_cyl(14, 2 * R, -R), make_cylinder(R - 2, 30, (0, 0, -15)))
piston = fuse(piston, boss)
piston = cut_all(
    piston,
    [
        x_cyl(10, 2 * R + 4, -R - 2),
        make_box(24, 2 * (R - 7), CH - 21 + SKIRT + 1, (-12, -(R - 7), -SKIRT - 1)),
    ]
    + [
        make_cylinder(BORE * 0.19, 3, (sx * VX, sy * (V_OFF + 4), CH - 1.6))
        for sx in (-1, 1)
        for sy in (-1, 1)
    ],
)
gudgeon = x_tube(10, 6.5, 2 * R - 10, -(R - 5))

BE = PIN_R + 7
BOLT_Y = PIN_R + 8
SE_R = 15.5
L = ROD_LENGTH
upper = common(x_cyl(BE, 22, -11), make_box(22, 2 * BE, BE, (-11, -BE, 0)))
upper = fuse_all([upper, make_box(22, 2 * (BOLT_Y + 7), 15, (-11, -BOLT_Y - 7, 0))])
z0, z1 = BE - 4, L - SE_R + 4
shank = extrude(yz_face([(-13, z0), (13, z0), (8, z1), (-8, z1)], -9), 18, (1, 0, 0))
pocket_pts = [(-9, BE + 6), (9, BE + 6), (4.5, L - SE_R - 3), (-4.5, L - SE_R - 3)]
pockets = [
    extrude(yz_face(pocket_pts, 3), 7, (1, 0, 0)),
    extrude(yz_face(pocket_pts, -10), 7, (1, 0, 0)),
]
rod = fuse_all([upper, shank, x_cyl(SE_R, 20, -10, 0, L)])
rod = cut_all(
    rod,
    pockets
    + [x_cyl(PIN_R, 30, -15), x_cyl(10, 30, -15, 0, L)]
    + [make_cylinder(4.3, 40, (0, s * BOLT_Y, -20)) for s in (-1, 1)],
)
cap = common(x_cyl(BE, 22, -11), make_box(22, 2 * BE, BE, (-11, -BE, -BE)))
cap = fuse(cap, make_box(22, 2 * (BOLT_Y + 7), 15, (-11, -BOLT_Y - 7, -15)))
cap = cut_all(
    cap, [x_cyl(PIN_R, 30, -15)] + [make_cylinder(4.3, 40, (0, s * BOLT_Y, -20)) for s in (-1, 1)]
)
rod_bolt = bolt(0, 0, -15, 4.0, 34, 12, 6, down=True)

for i in range(4):
    yp, zp, zpin, tilt = slider_crank(CRANK_ANGLE + PHASE[i])
    n = i + 1
    put(
        f"piston_{n}",
        piston,
        PISTON_C,
        (XC[i], 0, zpin),
        0,
        "ENG-150",
        {"material": "AlSi12CuNiMg, forged"},
    )
    put(
        f"gudgeon_pin_{n}",
        gudgeon,
        BRIGHT,
        (XC[i], 0, zpin),
        0,
        "ENG-151",
        {"material": "case-hardened 16MnCr5"},
    )
    put(
        f"conrod_{n}",
        rod,
        STEEL,
        (XC[i], yp, zp),
        tilt,
        "ENG-140",
        {"material": "forged C70S6, fracture-split"},
    )
    put(f"rod_cap_{n}", cap, STEEL, (XC[i], yp, zp), tilt, "ENG-141", {"material": "forged C70S6"})
    for s, side in ((-1, "a"), (1, "b")):
        put(
            f"rod_bolt_{n}{side}",
            translate(rod_bolt, (0, s * BOLT_Y, 0)),
            DARK,
            (XC[i], yp, zp),
            tilt,
            "ENG-143",
            {"material": "12.9 alloy steel"},
        )

# ================================================================== block
prof = [
    (-95, SKIRT_Z),
    (95, SKIRT_Z),
    (95, 35),
    (BW, 105),
    (BW, DECK_Z),
    (-BW, DECK_Z),
    (-BW, 105),
    (-95, 35),
]
block = extrude(yz_face(prof, XB0), XB1 - XB0, (1, 0, 0))
ribs = [make_box(10, 12, 90, (MAIN_X[k] - 5, -BW - 9, 40)) for k in range(5)]
ribs.append(make_box(70, 30, 70, (XC[3] - 35, -110, -20)))  # oil filter boss
block = join(block, ribs)
jacket_out = fuse_all([make_cylinder(LINER_R + 8, 111, (x, 0, DECK_Z - 110)) for x in XC])
jacket_in = fuse_all([make_cylinder(LINER_R, 113, (x, 0, DECK_Z - 111)) for x in XC])
# the water jacket and the four crank bays stand clear of one another, as do the bores
# and the main bearing bore
block = drill(
    block,
    [cut(jacket_out, jacket_in)]
    + [
        make_box(
            BORE_PITCH - MAIN_LEN + 4,
            2 * (CW_R + 6),
            40 - SKIRT_Z + 1,
            (MAIN_X[k] + MAIN_LEN / 2 - 2, -CW_R - 6, SKIRT_Z - 1),
        )
        for k in range(4)
    ],
)
block = drill(
    block,
    [make_cylinder(BORE / 2, DECK_Z - 29, (x, 0, 30)) for x in XC]
    + [x_cyl(MAIN_R + 0.5, XB1 - XB0 + 2, XB0 - 1)],
)
block = cut_all(
    block,
    [
        make_box(
            MAIN_X[4] - MAIN_X[0] + MAIN_LEN - 4,
            104,
            -SKIRT_Z + 1,
            (MAIN_X[0] - MAIN_LEN / 2 + 2, -52, SKIRT_Z - 1),
        ),
        make_cylinder(9, 30, (XC[3], 0, -45)),
    ],
)
block = cut(block, y_cyl(22, 40, XC[3], -125, 15))
if CUTAWAY:
    block = cut(
        block, make_box(XB1 - CUT_X + 2, 200, DECK_Z - SKIRT_Z + 2, (CUT_X, 0, SKIRT_Z - 1))
    )
part(
    "cylinder_block",
    block,
    color=ALU,
    part_number="ENG-100",
    properties={"material": "A319 aluminium, cast-in iron liners"},
)

main_cap = cut(
    make_box(MAIN_LEN - 4, 100, 40, (-(MAIN_LEN - 4) / 2, -50, -40)), x_cyl(MAIN_R + 0.5, 30, -15)
)
cap_bolt = bolt(0, 0, -40, 5.0, 60, 14, 7, down=True)
for k in range(5):
    put(
        f"main_cap_{k + 1}",
        main_cap,
        DARK,
        (MAIN_X[k], 0, 0),
        0,
        "ENG-105",
        {"material": "nodular cast iron"},
    )
    for s, lr in ((-1, "a"), (1, "b")):
        place(f"main_cap_bolt_{k + 1}{lr}", cap_bolt, at=(MAIN_X[k], s * 38, 0))
        identity(
            f"main_cap_bolt_{k + 1}{lr}",
            part_number="ENG-106",
            properties={"material": "10.9 steel"},
        )


# ================================================================== cylinder head
def along_valve(shape, x, side):
    """Put a shape built on +Z at the valve seat of the intake (+1) or exhaust (-1) valve at x."""
    return translate(
        rotate(shape, (0, 0, 0), (1, 0, 0), -side * VALVE_ANGLE), (x, side * V_OFF, DECK_Z)
    )


head = make_box(XB1 - XB0, 2 * HW, HEAD_H, (XB0, -HW, DECK_Z))
towers = [
    make_box(16, 52, ZC - DECK_Z - HEAD_H + 3, (MAIN_X[k] - 8, s * YC - 26, DECK_Z + HEAD_H - 2))
    for k in range(5)
    for s in (-1, 1)
]
head = join(head, towers)
# each line's tools stand clear of one another, so each line is one cut
head = drill(
    head,
    [make_cylinder(BORE / 2 - 1, 5, (x, 0, DECK_Z - 1)) for x in XC]  # chambers
    + [make_cylinder(12.5, HEAD_H, (x, 0, DECK_Z + 30)) for x in XC],
)  # plug wells
head = drill(
    head,
    [
        along_valve(make_cylinder(14.6, 120, (0, 0, 56)), x + sx * VX, side)  # tappet bores
        for x in XC
        for sx in (-1, 1)
        for side in (-1, 1)
    ],
)
head = drill(
    head,
    [x_cyl(14.5, XB1 - XB0 + 2, XB0 - 1, s * YC, ZC) for s in (-1, 1)]  # cam bores
    + [make_cylinder(7.5, HEAD_H + 5, (x, 0, DECK_Z - 1)) for x in XC],
)  # plug holes
head = drill(
    head,
    [y_cyl(15, 45, x, HW - 44, DECK_Z + 36) for x in XC]  # intake ports
    + [y_cyl(14, 45, x, -HW - 1, DECK_Z + 40) for x in XC],
)  # exhaust ports
if CUTAWAY:
    # open the intake side over the front two cylinders, leaving the cam bearing bulkheads standing
    window = make_box(XB1 + 2, HW, ZC - DECK_Z - 20, (0, 8, DECK_Z + 56))
    window = cut_all(
        window,
        [
            make_box(16, 52, ZC - DECK_Z, (MAIN_X[k] - 8, YC - 26, DECK_Z + 40))
            for k in range(5)
            if MAIN_X[k] > -9
        ],
    )
    head = cut(head, window)
part(
    "cylinder_head",
    head,
    color=ALU,
    part_number="ENG-200",
    properties={"material": "A356-T6 aluminium"},
)


# valvetrain: built once on +Z, placed along each inclined valve axis
def valve(r_head):
    return about_z([(0, -2), (r_head, -2), (r_head, -0.5), (4, 7), (3, 10), (3, 104), (0, 104)])


spring_prof = [(8.5, 58)]
z = 58.0
while z < 90:
    spring_prof += [(12.0, z + 1.2), (12.0, z + 2.4), (9.6, z + 3.4)]
    z += 3.4
spring_prof += [(12.0, z + 1), (12.0, z + 2), (8.5, z + 2)]
spring = about_z(spring_prof)
s_top = z + 2
retainer = about_z(
    [(3.2, s_top), (11.5, s_top), (11.5, s_top + 1.5), (6, s_top + 6), (3.2, s_top + 6)]
)
tappet = cut(make_cylinder(14, 12, (0, 0, 100)), make_cylinder(12, 9, (0, 0, 100)))
v_in, v_ex = valve(15.0), valve(13.0)
for i, x in enumerate(XC):
    for side, kind in ((1, "intake"), (-1, "exhaust")):
        for sx, lr in ((-1, "a"), (1, "b")):
            tag = f"{i + 1}{lr}"
            spot = dict(at=(x + sx * VX, side * V_OFF, DECK_Z), tilt=-side * VALVE_ANGLE)
            put(
                f"{kind}_valve_{tag}",
                v_in if side > 0 else v_ex,
                BRIGHT,
                **spot,
                part_number="ENG-210" if side > 0 else "ENG-211",
                properties={
                    "material": "X45CrSi9-3" if side > 0 else "X53CrMnNiN21-9, Stellite seat"
                },
            )
            put(
                f"{kind}_spring_{tag}",
                spring,
                "#3B6E8F",
                **spot,
                part_number="ENG-212",
                properties={"material": "Si-Cr spring steel"},
            )
            put(f"{kind}_retainer_{tag}", retainer, STEEL, **spot, part_number="ENG-213")
            put(f"{kind}_tappet_{tag}", tappet, BRIGHT, **spot, part_number="ENG-214")


# camshafts: base circle 17, lobe lift 8; half crank speed
def lobe_face(x0, yc, zc, ang):
    pts = []
    for k in range(LOBE):
        phi = 2 * math.pi * k / LOBE
        c = math.cos(phi)
        r = 17 + (8 * c**3 if c > 0 else 0)
        a = phi + math.radians(ang)
        pts.append((yc + r * math.cos(a), zc + r * math.sin(a)))
    return yz_face(pts, x0)


CAM_PHASE = [0.0, 270.0, 90.0, 180.0]
for side, kind in ((1, "intake"), (-1, "exhaust")):
    yc = side * YC
    bits = [x_cyl(12, FRONT + 16 - XB0 + 8, XB0 - 8, yc, ZC)]
    bits += [x_cyl(14, 16, MAIN_X[k] - 8, yc, ZC) for k in range(5)]
    base = -CRANK_ANGLE / 2 + (90 if side > 0 else -20)
    for i, x in enumerate(XC):
        for sx in (-1, 1):
            bits.append(
                extrude(lobe_face(x + sx * VX - 7, yc, ZC, base + CAM_PHASE[i]), 14, (1, 0, 0))
            )
    bits.append(x_cyl(16, 10, FRONT - 2, yc, ZC))
    part(
        f"{kind}_camshaft",
        join(bits[0], bits[1:]),
        color=STEEL,
        part_number=f"ENG-22{0 if side > 0 else 1}",
        properties={"material": "chilled cast iron, ground lobes"},
    )
    part(
        f"{kind}_cam_sprocket",
        sprocket(38, 44, 48, 12, FRONT + 2, 10, yc, ZC, holes=5),
        color=STEEL,
        part_number="ENG-225",
    )
    cam_cap = cut(make_box(16, 52, 15, (-8, -26, 0)), x_cyl(14.5, 20, -10))
    cap_b = bolt(0, 0, 15, 4.0, 40, 11, 5)
    for k in range(5):
        put(
            f"{kind}_cam_cap_{k + 1}",
            cam_cap,
            ALU,
            (MAIN_X[k], yc, ZC),
            0,
            "ENG-226",
            {"material": "A356-T6 aluminium"},
        )
        for s, lr in ((-1, "a"), (1, "b")):
            place(f"{kind}_cam_cap_bolt_{k + 1}{lr}", cap_b, at=(MAIN_X[k], yc + s * 19, ZC))
            identity(
                f"{kind}_cam_cap_bolt_{k + 1}{lr}",
                part_number="ENG-227",
                properties={"material": "10.9 steel, zinc flake"},
            )

chain = band([(YC, ZC, 46), (-YC, ZC, 46), (0, 0, 24)], FRONT + 2.5, 9, 0.5, 6)
part(
    "timing_chain",
    chain,
    color="#8E949A",
    part_number="ENG-230",
    properties={"material": "simplex roller chain 3/8 in"},
)
guide = extrude(
    yz_face([(YC + 52, ZC - 10), (YC + 57, ZC - 10), (31, 40), (26, 40)], FRONT + 13), 4, (1, 0, 0)
)
part(
    "chain_guide",
    guide,
    color=BLACK,
    part_number="ENG-231",
    properties={"material": "PA46 on steel"},
)

# cam cover, spark plugs, coils
cz0 = DECK_Z + HEAD_H
cov_h = 62.0
cover = make_box(XB1 - XB0 - 6, 2 * (HW - 4), cov_h, (XB0 + 3, -(HW - 4), cz0))
try:
    cover = fillet(cover, 14, [e for e in edges(cover) if bounding_box(e)[1][2] > cz0 + 1])
except FilletError:
    pass
try:
    cover = hollow_facing(cover, 4.0, [(0, 0, -1)])
except HollowError:
    cover = cut(
        cover, make_box(XB1 - XB0 - 14, 2 * (HW - 8), cov_h - 4, (XB0 + 7, -(HW - 8), cz0 - 1))
    )
lip = cut(
    make_box(XB1 - XB0 - 2, 2 * (HW - 1), 6, (XB0 + 1, -(HW - 1), cz0)),
    make_box(XB1 - XB0 - 12, 2 * (HW - 7), 8, (XB0 + 6, -(HW - 7), cz0 - 1)),
)
cover = fuse(cover, lip)
for s in (-1, 1):
    cover = fuse(cover, make_box(XB1 - XB0 - 60, 6, 5, (XB0 + 30, s * 30 - 3, cz0 + cov_h - 1)))
cover = drill(cover, [make_cylinder(13, cov_h + 10, (x, 0, cz0)) for x in XC])
try:
    cover = fuse(
        cover,
        text3d(
            "DOHC 16V",
            16,
            2,
            plane=Plane.XY.offset(cz0 + cov_h - 0.5),
            at=(XB0 + 30, -50),
            align="left",
        ),
    )
except Exception:
    pass
if CUTAWAY:
    cover = cut(cover, make_box(XB1 + 20, 2 * HW + 40, cov_h + 20, (0, -HW - 20, cz0 - 5)))
part(
    "cam_cover",
    cover,
    color=RED,
    part_number="ENG-240",
    properties={"material": "die-cast magnesium, powder coat"},
)
cb = bolt(0, 0, cz0 + 6, 3.0, 12, 10, 5)
for s, lr in ((-1, "a"), (1, "b")):
    for k, b in enumerate(
        linear_pattern(translate(cb, (XB0 + 14, s * (HW - 4), 0)), (60, 0, 0), 7)
    ):
        if CUTAWAY and XB0 + 14 + 60 * k > -4:
            continue
        part(f"cover_bolt_{lr}{k + 1}", b, color=DARK, part_number="ENG-241")

plug = fuse_all(
    [
        make_cylinder(7, 24, (0, 0, 2)),
        hex_prism(16, 12, 0, 0, 25.5),
        make_cylinder(9.5, 3, (0, 0, 37)),
    ]
)
insulator = fuse(make_cylinder(6, 50, (0, 0, 36)), make_cone(6, 3.5, 8, (0, 0, 85.5)))
coil = fuse_all(
    [
        make_cylinder(11, cz0 + cov_h - DECK_Z - 84, (0, 0, 86)),
        make_box(46, 30, 24, (-23, -15, cz0 + cov_h - DECK_Z - 4)),
        make_box(16, 22, 14, (-8, 15 - 2, cz0 + cov_h - DECK_Z + 2)),
    ]
)
for i, x in enumerate(XC):
    put(
        f"spark_plug_{i + 1}",
        plug,
        BRIGHT,
        (x, 0, DECK_Z),
        0,
        "ENG-250",
        {"material": "nickel-plated steel, iridium tip"},
    )
    put(
        f"plug_insulator_{i + 1}",
        insulator,
        "#F2F0EA",
        (x, 0, DECK_Z),
        0,
        "ENG-250",
        {"material": "alumina ceramic"},
    )
    put(
        f"ignition_coil_{i + 1}",
        coil,
        BLACK,
        (x, 0, DECK_Z),
        0,
        "ENG-251",
        {"material": "PBT-GF30 housing"},
    )

# ================================================================== oil sump
SD = 82.0
sp = [
    (-95, SKIRT_Z + 1),
    (95, SKIRT_Z + 1),
    (95, SKIRT_Z - 14),
    (80, SKIRT_Z - SD),
    (-80, SKIRT_Z - SD),
    (-95, SKIRT_Z - 14),
]
sump = extrude(yz_face(sp, XB0 + 2), XB1 - XB0 - 4, (1, 0, 0))
sump = fuse(sump, make_box(XB1 - XB0, 206, 7, (XB0, -103, SKIRT_Z - 7)))
spi = [
    (-89, SKIRT_Z + 2),
    (89, SKIRT_Z + 2),
    (89, SKIRT_Z - 14),
    (75, SKIRT_Z - SD + 5),
    (-75, SKIRT_Z - SD + 5),
    (-89, SKIRT_Z - 14),
]
sump = cut(sump, extrude(yz_face(spi, XB0 + 7), XB1 - XB0 - 14, (1, 0, 0)))
sump_ribs = [make_box(6, 150, 7, (x - 3, -75, SKIRT_Z - SD - 6)) for x in (-120, -40, 40, 120)]
for s in (-1, 1):
    rib = [
        (s * 94, SKIRT_Z - 8),
        (s * 101, SKIRT_Z - 8),
        (s * 86, SKIRT_Z - SD + 6),
        (s * 79, SKIRT_Z - SD + 6),
    ]
    sump_ribs += [extrude(yz_face(rib, x - 3), 6, (1, 0, 0)) for x in XC]
sump = join(sump, sump_ribs)
part(
    "oil_sump",
    sump,
    color="#5F6368",
    part_number="ENG-300",
    properties={"material": "die-cast aluminium, painted"},
)
part(
    "drain_plug",
    bolt(60, 30, SKIRT_Z - SD, 7, 14, 17, 7, down=True),
    color=STEEL,
    part_number="ENG-301",
)
part(
    "oil_filter",
    fuse(y_cyl(38, 86, XC[3], -125 - 86 + 2, 15), y_cyl(34, 6, XC[3], -125 - 86 - 3, 15)),
    color="#1A3A6B",
    part_number="ENG-310",
    properties={"material": "spin-on cartridge"},
)

# ============================================================== intake: swept runners into a plenum
# With CUTAWAY the front quarter (x > 0, intake side) of the manifold is taken away with
# the head
# section, so the front two cylinders' valves show.
zp = DECK_Z + 36
A = math.radians(52)
RR = 45.0
p1 = (HW + 14, zp)
cen = (p1[0], zp + RR)
p2 = (cen[0] + RR * math.sin(A), cen[1] - RR * math.cos(A))
pm = (cen[0] + RR * math.sin(A / 2), cen[1] - RR * math.cos(A / 2))
p3 = (p2[0] + 95 * math.cos(A), p2[1] + 95 * math.sin(A))
PY, PZ = p3[0] + 22 * math.cos(A), p3[1] + 22 * math.sin(A)
quarter = make_box(XB1 + 200, 600, 600, (0, 0, -200))
flange_in = cut_all(
    make_box(XB1 - XB0 - 16, 10, 42, (XB0 + 8, HW - 1, DECK_Z + 14)),
    [y_cyl(14, 14, x, HW - 3, zp) for x in XC],
)
part(
    "intake_flange",
    cut(flange_in, quarter) if CUTAWAY else flange_in,
    color=BLACK,
    part_number="ENG-400",
)
for i, x in enumerate(XC):
    if CUTAWAY and x > 0:
        continue
    sk = Sketch(Plane((x, 0, 0), (1, 0, 0), (0, 1, 0)))
    path = sk.move_to((HW - 4, zp)).line_to(p1).arc_via(pm, p2).line_to(p3).path()
    face = (
        Sketch(Plane((x, HW - 4, zp), (0, 1, 0), (1, 0, 0)))
        .circle((0, 0), 17)
        .circle((0, 0), 13.5)
        .face()
    )
    part(
        f"intake_runner_{i + 1}",
        sweep(face, path),
        color=BLACK,
        part_number="ENG-401",
        properties={"material": "PA6-GF30"},
    )
PX0, PX1 = XC[0] - 50, XC[3] + 50


def plenum_profile(r, r_neck, x_end, x_neck):
    """(x, r) half-section of the plenum: a drum whose domed end runs into the throttle neck."""
    a_end = math.degrees(math.asin(r_neck / r))
    dome = [
        (PX0 - r * math.sin(math.radians(a)), r * math.cos(math.radians(a)))
        for a in range(0, 91, 10)
        if math.cos(math.radians(a)) * r > r_neck
    ]
    return (
        [(x_end, 0), (x_end, r)]
        + dome
        + [(PX0 - r * math.cos(math.radians(a_end)), r_neck), (x_neck, r_neck), (x_neck, 0)]
    )


# with CUTAWAY the plenum stops, open, at the section plane; otherwise it is closed by a flat end
xe_out, xe_in = (0.0, 1.0) if CUTAWAY else (PX1 + 4, PX1)
plen = cut(
    about_x(plenum_profile(44, 36, xe_out, PX0 - 76)),
    about_x(plenum_profile(40, 28, xe_in, PX0 - 80)),
)
part(
    "intake_plenum",
    translate(plen, (0, PY, PZ)),
    color=BLACK,
    part_number="ENG-402",
    properties={"material": "PA6-GF30"},
)
tb = fuse_all([x_tube(34, 26, 40, PX0 - 120, PY, PZ), x_cyl(40, 6, PX0 - 86, PY, PZ)])
tb = cut(tb, x_cyl(26, 60, PX0 - 125, PY, PZ))
part(
    "throttle_body",
    tb,
    color=ALU,
    part_number="ENG-405",
    properties={"material": "die-cast aluminium"},
)
part(
    "throttle_plate",
    rotate(x_cyl(25.5, 1.5, PX0 - 101, PY, PZ), (PX0 - 100, PY, PZ), (0, 0, 1), 60),
    color=BRIGHT,
    part_number="ENG-406",
)

# port fuel injection: one injector in the top of each runner, fed from a common rail
YI, ZI = HW + 16, zp + 15
injector = fuse_all(
    [
        make_cylinder(5, 12, (0, 0, -6)),
        make_cylinder(8, 22, (0, 0, 5)),
        make_cylinder(6.5, 14, (0, 0, 26)),
        make_box(14, 16, 10, (-7, 4, 12)),
    ]
)
injector = cut(injector, make_box(20, 2, 2, (-10, -9, 18)))
rail_x0 = XB0 + 24
rail_x1 = -6.0 if CUTAWAY else XC[3] + 40
rail_z = ZI + 46
for i, x in enumerate(XC):
    if CUTAWAY and x > 0:
        continue
    put(
        f"fuel_injector_{i + 1}",
        injector,
        "#2E4A62",
        (x, YI, ZI),
        0,
        "ENG-410",
        {"material": "multi-hole solenoid injector"},
    )
rail = cut(
    x_cyl(10, rail_x1 - rail_x0, rail_x0, YI, rail_z),
    x_cyl(6, rail_x1 - rail_x0 + 2, rail_x0 - 1, YI, rail_z),
)
end_fitting = about_x(
    [
        (rail_x0 - 12, 0),
        (rail_x0 + 1, 0),
        (rail_x0 + 1, 10),
        (rail_x0 - 4, 10),
        (rail_x0 - 4, 7),
        (rail_x0 - 12, 7),
    ]
)
rail = fuse(rail, translate(end_fitting, (0, YI, rail_z)))
part(
    "fuel_rail",
    rail,
    color=BRIGHT,
    part_number="ENG-411",
    properties={"material": "304 stainless, brazed cups"},
)
for k, xb in enumerate([XC[0] - 45, XC[1] - 45] + ([] if CUTAWAY else [XC[2] - 45, XC[3] + 45])):
    br = cut(
        make_box(12, YI - HW + 4, 16, (xb - 6, HW, rail_z - 8)), x_cyl(10.2, 14, xb - 7, YI, rail_z)
    )
    part(
        f"rail_bracket_{k + 1}",
        br,
        color=DARK,
        part_number="ENG-412",
        properties={"material": "S355 steel, zinc"},
    )

# ================================================================== exhaust: 4-into-1 header
zx = DECK_Z + 40
part(
    "exhaust_flange",
    cut_all(
        make_box(XB1 - XB0 - 16, 10, 44, (XB0 + 8, -HW - 9, zx - 22)),
        [y_cyl(15.5, 14, x, -HW - 12, zx) for x in XC],
    ),
    color=BLUED,
    part_number="ENG-500",
)
XCOL, YCOL, ZQ = 0.0, -HW - 72, 40.0
offsets = [(-16, -16), (-16, 16), (16, 16), (16, -16)]
down = (0.0, 0.0, -1.0)
for i, x in enumerate(XC):
    t0 = (0.0, -1.0, 0.0)
    p_0 = (x, -HW + 4, zx)
    p_1 = v_add(p_0, v_mul(t0, 22))
    q = (XCOL + offsets[i][0], YCOL + offsets[i][1], ZQ)
    d = v_unit(v_sub(q, p_1))
    for _ in range(12):
        p_2 = bend_end(p_1, t0, d, 40)
        p_3 = v_sub(q, v_sub(bend_end((0, 0, 0), d, down, 70), (0, 0, 0)))
        d = v_unit(v_sub(p_3, p_2))
    q2 = v_add(q, (0, 0, -18))
    path = [
        line_edge(p_0, p_1),
        arc_edge(p_1, t0, p_2),
        line_edge(p_2, p_3),
        arc_edge(p_3, d, q),
        line_edge(q, q2),
    ]
    try:
        primary = pipe(path, p_0, t0, 15, 12.5)
    except Exception:
        pts = [p_0, p_1, p_2, p_3, q, q2]
        segs = []
        for a, b in zip(pts, pts[1:], strict=False):
            seg_len = math.sqrt(v_dot(v_sub(b, a), v_sub(b, a)))
            dd = v_unit(v_sub(b, a))
            cyl = make_cylinder(15, seg_len)
            ang = math.degrees(math.acos(max(-1, min(1, dd[2]))))
            if abs(ang) > 1e-6 and abs(ang - 180) > 1e-6:
                cyl = rotate(cyl, (0, 0, 0), v_unit((-dd[1], dd[0], 0)), ang)
            segs.append(fuse(translate(cyl, a), make_sphere(15, b)))
        primary = fuse_all(segs)
    part(
        f"exhaust_primary_{i + 1}",
        primary,
        color=BLUED,
        part_number="ENG-501",
        properties={"material": "304 stainless, 38 x 2.5 mm"},
    )
coll = cut(
    make_cone(44, 27, 70, (XCOL, YCOL, ZQ - 80)), make_cone(41, 24, 72, (XCOL, YCOL, ZQ - 81))
)
coll = rotate(coll, (XCOL, YCOL, ZQ - 45), (1, 0, 0), 180)
part(
    "exhaust_collector",
    coll,
    color=BLUED,
    part_number="ENG-502",
    properties={"material": "304 stainless"},
)
c0 = (XCOL, YCOL, ZQ - 78)
c1 = (XCOL, YCOL, ZQ - 100)
c2 = bend_end(c1, down, (-1.0, 0.0, 0.0), 60)
c3 = (XB0 - 160, YCOL, c2[2])
down_pipe = pipe([line_edge(c0, c1), arc_edge(c1, down, c2), line_edge(c2, c3)], c0, down, 26, 23)
part(
    "exhaust_downpipe",
    down_pipe,
    color=BLUED,
    part_number="ENG-503",
    properties={"material": "409 stainless"},
)

# ================================================================== accessory drive
AY, AZ = -150.0, 115.0
alt = fuse_all(
    [
        x_cyl(56, 96, FRONT - 74, AY, AZ),
        x_cyl(59, 8, FRONT - 74, AY, AZ),
        x_cyl(59, 8, FRONT + 14, AY, AZ),
        x_cyl(16, 14, FRONT + 20, AY, AZ),
    ]
)
alt = cut_all(alt, [x_tube(62, 53, 5, FRONT - 60 + 12 * k, AY, AZ) for k in range(6)])
part(
    "alternator",
    alt,
    color=BRIGHT,
    part_number="ENG-600",
    properties={"material": "die-cast aluminium"},
)
apul = about_x([(pul_x, 8), (pul_x + 30, 8), (pul_x + 30, 30), (pul_x, 30)])
part("alternator_pulley", translate(apul, (0, AY, AZ)), color=DARK, part_number="ENG-601")
part(
    "alternator_bracket",
    make_box(40, -AY - BW + 30, 50, (FRONT - 60, AY, 30)),
    color=ALU,
    part_number="ENG-602",
)
part(
    "drive_belt",
    band([(0, 0, 62), (AY, AZ, 30)], pul_x + 2, 26, -1, 5),
    color=BLACK,
    part_number="ENG-610",
    properties={"material": "EPDM 6PK poly-V"},
)

# ================================================= mates: the pulley and flywheel ride on the crank
for args in (
    ("crank_pulley", "hole 1", "crankshaft", "cylinder 1", "concentric"),
    ("flywheel", ">X", "crankshaft", "<X", "coincident"),
):
    try:
        mate(*args)
    except Exception:
        pass
