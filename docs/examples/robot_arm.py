# SPDX-License-Identifier: Apache-2.0
"""A six-axis industrial robot arm in a working pose, with a parallel gripper.

A mid-size articulated robot (about 10 kg payload, 1.4 m reach) built as a
showcase of machined and cast components: a floor plate with mated anchor
studs, a ribbed base casting, the J1 turntable, a lofted shoulder housing with
the J2 gearbox and servo, a tapered upper arm with ribbed pockets, the elbow
with its J3 servo, the J4 roll forearm, the J5/J6 wrist with an ISO 9409-1
50-4-M6 tool flange, and a two-finger parallel gripper holding a turned part.
Servos have cooling fins and connector boxes, the cable harness is swept along
a filleted path, and every joint carries its bolt circle. Each link is built
in the zero pose and turned about its joint axes by J1 to J6, so changing one
angle re-poses everything downstream of it.

Tags: solid, assembly, mates, sketch, showcase
"""

# ---------------------------------------------------------------- pose (degrees)
J1 = -30.0  # base rotation, about +Z
J2 = 32.0  # shoulder, about +Y (positive leans the upper arm forward)
J3 = -52.0  # elbow, about +Y (negative raises the forearm)
J4 = 15.0  # forearm roll, about the forearm axis
J5 = 75.0  # wrist bend, about +Y in the wrist
J6 = 25.0  # tool flange roll

# ---------------------------------------------------------------- main dimensions (mm)
PLATE_SIZE = 560.0  # square floor plate
PLATE_T = 28.0
ANCHOR_PITCH = 450.0  # anchor stud square
BASE_R = 205.0  # base casting radius at the foot
BASE_H = 235.0
TURNTABLE_R = 185.0
TURNTABLE_T = 70.0
SHOULDER_X = 150.0  # J2 axis offset from J1
SHOULDER_Z = 620.0  # J2 axis height above the floor
UPPER_ARM = 640.0  # J2 to J3
ARM_Y = 150.0  # upper arm centre plane, off the robot's centre line
ARM_T = 110.0  # upper arm thickness
FOREARM_RISE = 140.0  # J3 to the J4 axis
FOREARM = 700.0  # J3 to J5 along the forearm
WRIST = 100.0  # J5 to the tool flange face
FLANGE_PCD = 50.0  # ISO 9409-1-50-4-M6
FLANGE_D = 63.0
GRIP_OPEN = 52.0  # gap between the finger pads = workpiece diameter
FINGER_LEN = 105.0
MOTOR_R = 62.0  # J2 servo radius; the others scale from it

# ---------------------------------------------------------------- colours
CAST = "#E8E8E8"  # painted castings
ACCENT = "#FF6F00"  # covers and caps
MOTOR = "#1E1F22"
MOTOR_CAP = "#34373C"
MACHINED = "#BFC3C8"
SCREW = "#2A2C30"
PLATE = "#4B5157"
HARNESS = "#202020"
GRIPPER = "#3A3F46"
WORKPIECE = "#C9A54A"

# ---------------------------------------------------------------- joint frames (zero pose)
BASE_TOP = PLATE_T + BASE_H
TT_TOP = BASE_TOP + TURNTABLE_T
SX, SZ = SHOULDER_X, SHOULDER_Z
J3Z = SZ + UPPER_ARM
J4Z = J3Z + FOREARM_RISE
J5X = SX + FOREARM
FLANGE_X = J5X + WRIST
JOINTS = [
    ((0.0, 0.0, 0.0), (0, 0, 1), J1),
    ((SX, 0.0, SZ), (0, 1, 0), J2),
    ((SX, 0.0, J3Z), (0, 1, 0), J3),
    ((0.0, 0.0, J4Z), (1, 0, 0), J4),
    ((J5X, 0.0, J4Z), (0, 1, 0), J5),
    ((0.0, 0.0, J4Z), (1, 0, 0), J6),
]


def pose(shape, link):
    """A shape of link `link` (0 = the fixed base) moved from the zero pose into the pose."""
    for point, axis, angle in reversed(JOINTS[:link]):
        if angle:
            shape = rotate(shape, point, axis, angle)
    return shape


def add(name, shape, link, color, part_number=None, material=None):
    props = {"material": material} if material else None
    return part(name, pose(shape, link), color=color, part_number=part_number, properties=props)


def soft_fillet(shape, r, picked=None):
    """A fillet when OCCT will build it, the sharp shape when it will not."""
    try:
        return fillet(shape, r, picked) if picked is not None else fillet_all(shape, r)
    except Exception:
        return shape


def soft_chamfer(shape, d, picked):
    try:
        return chamfer(shape, d, picked)
    except Exception:
        return shape


# ---------------------------------------------------------------- shape helpers
def xcyl(r, x0, x1, y=0.0, z=0.0):
    return translate(rotate(make_cylinder(r, x1 - x0), (0, 0, 0), (0, 1, 0), 90), (x0, y, z))


def ycyl(r, y0, y1, x=0.0, z=0.0):
    return translate(rotate(make_cylinder(r, y1 - y0), (0, 0, 0), (1, 0, 0), -90), (x, y0, z))


def orient(shape, d):
    """Turn a shape built along local +Z so that +Z points along `d` (+x, -x, +y, -y, +z, -z)."""
    turns = {
        "+z": None,
        "-z": ((1, 0, 0), 180),
        "+x": ((0, 1, 0), 90),
        "-x": ((0, 1, 0), -90),
        "+y": ((1, 0, 0), -90),
        "-y": ((1, 0, 0), 90),
    }[d]
    return shape if turns is None else rotate(shape, (0, 0, 0), turns[0], turns[1])


def put(shape, d, at):
    return translate(orient(shape, d), at)


def rrect(plane, cx, cy, w, h, r):
    return Sketch(plane).rounded_rectangle((cx - w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), r)


def hexagon(across, thick):
    r = across / math.sqrt(3)
    return extrude(
        polygon_face(
            [
                (r * math.cos(math.radians(60 * k + 30)), r * math.sin(math.radians(60 * k + 30)))
                for k in range(6)
            ]
        ),
        thick,
    )


_SCREWS = {}


def cap_screw(d):
    """ISO 4762 socket head cap screw, head seated on z = 0, shank down into the part."""
    if d not in _SCREWS:
        head = make_cylinder(0.8 * d, d)
        head = soft_chamfer(
            head, 0.08 * d, [e for e in edges(head) if bounding_box(e)[1][2] > d - 1e-6]
        )
        screw = fuse(head, make_cylinder(d / 2, 1.6 * d, (0, 0, -1.5 * d)))
        _SCREWS[d] = cut(screw, translate(hexagon(0.86 * d, 0.6 * d), (0, 0, 0.42 * d)))
    return _SCREWS[d]


def screw_ring(d, n, pcd, d_out, at, phase=0.0):
    """n cap screws on a circle of diameter pcd, heads facing d_out, centred on `at`."""
    out = []
    for k in range(n):
        a = math.radians(phase + 360.0 * k / n)
        s = translate(cap_screw(d), (pcd / 2 * math.cos(a), pcd / 2 * math.sin(a), 0))
        out.append(put(s, d_out, at))
    return out


def servo(R, L, spin=0.0):
    """A finned AC servo along local +Z from its mounting face at z = 0: (suffix, shape, colour)."""
    side = 2 * R + 22
    flange = extrude(rrect(Plane.XY, 0, 0, side, side, 10).face(), 14)
    pts = [(0, 13), (R, 13), (R, 0.22 * L)]
    z = 0.22 * L
    while z + 14 < 0.86 * L:
        pts += [(R + 8, z + 2), (R + 8, z + 7), (R, z + 9), (R, z + 14)]
        z += 14
    pts += [(R, L - 6), (R - 6, L), (0, L)]
    body = revolve(polygon_face(pts, Plane.XZ), (0, 0, 0), (0, 0, 1))
    cap = make_cylinder(R - 7, 38, (0, 0, L - 1))
    cap = soft_chamfer(cap, 4, [e for e in edges(cap) if bounding_box(e)[1][2] > L + 36])
    parts = [("flange", flange, MOTOR), ("body", body, MOTOR), ("encoder", cap, MOTOR_CAP)]
    for k, zc in enumerate((L - 0.62 * R - 30, L - 0.62 * R + 22)):
        box = make_box(42, 44, 40, (R - 12, -22, zc - 20))
        plug = xcyl(12, R + 29, R + 52, 0, zc)
        nut = translate(hexagon(30, 6), (0, 0, 0))
        nut = translate(rotate(nut, (0, 0, 0), (0, 1, 0), 90), (R + 29, 0, zc))
        parts += [
            (f"connector_box_{k + 1}", box, MOTOR),
            (f"plug_{k + 1}", fuse(nut, plug), MACHINED),
        ]
    screws = [
        translate(cap_screw(8), (sx * (side / 2 - 13), sy * (side / 2 - 13), 14))
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]
    parts += [(f"flange_screw_{k + 1}", s, SCREW) for k, s in enumerate(screws)]
    if spin:
        parts = [(n, rotate(s, (0, 0, 0), (0, 0, 1), spin), c) for n, s, c in parts]
    return parts


def add_servo(prefix, R, L, d, at, link, spin=0.0, rating="1.5 kW"):
    for suffix, s, c in servo(R, L, spin):
        pn = f"SRV-{int(R)}-{int(L)}" if suffix == "body" else None
        add(
            f"{prefix}_{suffix}",
            put(s, d, at),
            link,
            c,
            part_number=pn,
            material="AC servo, " + rating if suffix == "body" else None,
        )


def filleted_path(sketch, pts, r):
    """An open path through pts with each inner corner rounded to radius r (tangent arcs)."""
    sketch.move_to(pts[0])
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        a = (p0[0] - p1[0], p0[1] - p1[1])
        b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a, b = (a[0] / la, a[1] / la), (b[0] / lb, b[1] / lb)
        half = math.acos(max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))) / 2
        t = r / math.tan(half)
        bis = (a[0] + b[0], a[1] + b[1])
        lbis = math.hypot(*bis)
        c = (p1[0] + bis[0] / lbis * r / math.sin(half), p1[1] + bis[1] / lbis * r / math.sin(half))
        mid = (c[0] - bis[0] / lbis * r, c[1] - bis[1] / lbis * r)
        sketch.line_to((p1[0] + a[0] * t, p1[1] + a[1] * t))
        sketch.arc_via(mid, (p1[0] + b[0] * t, p1[1] + b[1] * t))
    sketch.line_to(pts[-1])
    return sketch.path()


def harness(prefix, y, pts, r_bend, link, clamps):
    """A cable harness swept along a filleted path in the plane at y, with clamp rings."""
    plane = Plane((0, y, 0), (0, -1, 0), (1, 0, 0))
    path = filleted_path(Sketch(plane), pts, r_bend)
    dx, dz = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    ln = math.hypot(dx, dz)
    start = Plane((pts[0][0], y, pts[0][1]), (dx / ln, 0, dz / ln), (0, 1, 0))
    try:
        tube = sweep(Sketch(start).circle((0, 0), 15).face(), path)
    except Exception:
        tube = fuse_all(
            [
                rotate(
                    make_cylinder(15, math.hypot(q[0] - p[0], q[1] - p[1]), (p[0], y, p[1])),
                    (p[0], y, p[1]),
                    (0, 1, 0),
                    math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])),
                )
                for p, q in zip(pts, pts[1:], strict=False)
            ]
            + [make_sphere(15, (p[0], y, p[1])) for p in pts[1:-1]]
        )
    add(
        f"{prefix}",
        tube,
        link,
        HARNESS,
        part_number="HRN-CORR-29",
        material="PA6 corrugated conduit",
    )
    gland = fuse(make_cylinder(19, 16), translate(hexagon(44, 10), (0, 0, 15)))
    for k, (p, q) in enumerate(((pts[1], pts[0]), (pts[-2], pts[-1]))):
        ang = math.degrees(math.atan2(q[0] - p[0], q[1] - p[1]))
        g = translate(
            rotate(rotate(gland, (0, 0, 0), (0, 0, 1), 0), (0, 0, 0), (0, 1, 0), ang + 180),
            (q[0], y, q[1]),
        )
        add(f"{prefix}_gland_{k + 1}", g, link, MACHINED, part_number="GLD-M40")
    for k, (seg, f) in enumerate(clamps):
        p, q = pts[seg], pts[seg + 1]
        cx, cz = p[0] + f * (q[0] - p[0]), p[1] + f * (q[1] - p[1])
        ang = math.degrees(math.atan2(q[0] - p[0], q[1] - p[1]))
        ring = cut(make_cylinder(20, 18, (0, 0, -9)), make_cylinder(15.5, 18, (0, 0, -9)))
        ring = translate(rotate(ring, (0, 0, 0), (0, 1, 0), ang), (cx, y, cz))
        add(f"{prefix}_clamp_{k + 1}", ring, link, MACHINED, part_number="CLP-29")


# ================================================================ 0  floor plate and base (fixed)
plate = extrude(rrect(Plane.XY, 0, 0, PLATE_SIZE, PLATE_SIZE, 40).face(), PLATE_T)
anchors = [(sx * ANCHOR_PITCH / 2, sy * ANCHOR_PITCH / 2) for sx in (-1, 1) for sy in (-1, 1)]
plate = cut_all(plate, [make_cylinder(13, PLATE_T, (x, y, 0)) for x, y in anchors])
plate = soft_chamfer(
    plate,
    3,
    [
        e
        for e in edges(plate)
        if bounding_box(e)[1][2] > PLATE_T - 1e-6
        and bounding_box(e)[1][0] - bounding_box(e)[0][0] > 100
    ],
)
part(
    "floor_plate",
    plate,
    color=PLATE,
    part_number="RB-100-FP",
    properties={"material": "S355 plate, painted"},
)

stud = fuse_all(
    [
        make_cylinder(10, 110, (0, 0, -70)),
        make_cylinder(20, 4),
        translate(hexagon(30, 16), (0, 0, 4)),
    ]
)
stud = fuse(stud, make_cone(10, 7, 4, (0, 0, 40)))
for k, (x, y) in enumerate(anchors):
    name = f"anchor_stud_{k + 1}"
    part(
        name,
        translate(stud, (x, y, PLATE_T)),
        color=MACHINED,
        part_number="ANC-M20x180",
        properties={"material": "8.8 zinc plated", "torque": "120 N m"},
    )
    try:
        mate(name, "cylinder 1", "floor_plate", f"hole {k + 1}", "concentric")
        mate(name, "<Z 2", "floor_plate", ">Z", "coincident")
    except Exception:
        pass

base_pts = [
    (0, PLATE_T - 1),
    (BASE_R + 22, PLATE_T - 1),
    (BASE_R + 22, PLATE_T + 32),
    (BASE_R - 4, PLATE_T + 36),
    (BASE_R - 22, PLATE_T + 110),
    (TURNTABLE_R - 12, BASE_TOP - 70),
    (TURNTABLE_R - 12, BASE_TOP - 14),
    (TURNTABLE_R - 2, BASE_TOP - 10),
    (TURNTABLE_R - 2, BASE_TOP),
    (0, BASE_TOP),
]
base = revolve(polygon_face(base_pts, Plane.XZ), (0, 0, 0), (0, 0, 1))
gusset = extrude(
    polygon_face(
        [
            (BASE_R - 30, PLATE_T + 20),
            (BASE_R + 20, PLATE_T + 20),
            (BASE_R + 20, PLATE_T + 34),
            (BASE_R - 14, PLATE_T + 130),
            (BASE_R - 30, PLATE_T + 130),
        ],
        Plane((0, -7, 0), (0, -1, 0), (1, 0, 0)),
    ),
    14,
    (0, 1, 0),
)
base = fuse_all([base] + circular_pattern(gusset, (0, 0, 0), (0, 0, 1), 8))
part(
    "base_casting",
    base,
    color=CAST,
    part_number="RB-110-BC",
    properties={"material": "EN-GJS-400 painted"},
)
for k, s in enumerate(screw_ring(12, 8, 2 * BASE_R + 22, "+z", (0, 0, PLATE_T + 32), phase=22.5)):
    part(f"base_screw_{k + 1}", s, color=SCREW, part_number="ISO4762-M12x40")
part(
    "j1_bearing_seal",
    cut(
        make_cylinder(TURNTABLE_R + 2, 14, (0, 0, BASE_TOP - 6)),
        make_cylinder(TURNTABLE_R - 20, 14, (0, 0, BASE_TOP - 6)),
    ),
    color=MACHINED,
    part_number="RB-111-SL",
)
panel = make_box(16, 150, 110, (-BASE_R - 4, -75, PLATE_T + 70))
part(
    "connector_panel",
    soft_fillet(panel, 4, edges_parallel_to(panel, (1, 0, 0))),
    color=ACCENT,
    part_number="RB-112-CP",
)
for k, y in enumerate((-36.0, 36.0)):
    plug = fuse_all(
        [
            xcyl(26, -BASE_R - 10, -BASE_R - 2, y, PLATE_T + 125),
            xcyl(20, -BASE_R - 40, -BASE_R - 8, y, PLATE_T + 125),
        ]
    )
    plug = cut(plug, xcyl(13, -BASE_R - 41, -BASE_R - 25, y, PLATE_T + 125))
    place(f"base_connector_{k + 1}", plug, part=None)
    identity(
        f"base_connector_{k + 1}",
        part_number="CON-M40-19P",
        properties={"material": "nickel brass"},
    )
for k, (y, z) in enumerate(
    [(-62, PLATE_T + 82), (62, PLATE_T + 82), (-62, PLATE_T + 168), (62, PLATE_T + 168)]
):
    part(
        f"panel_screw_{k + 1}",
        put(cap_screw(5), "-x", (-BASE_R - 4, y, z)),
        color=SCREW,
        part_number="ISO4762-M5x12",
    )

# ================================================================ 1  turntable and shoulder (J1)
tt = make_cylinder(TURNTABLE_R, TURNTABLE_T, (0, 0, BASE_TOP))
tt = soft_chamfer(tt, 6, [e for e in edges(tt) if bounding_box(e)[1][2] > TT_TOP - 1e-6])
add("turntable", tt, 1, CAST, part_number="RB-120-TT", material="EN-GJS-400 painted")
for k, s in enumerate(screw_ring(10, 12, 2 * (TURNTABLE_R - 15), "+z", (0, 0, TT_TOP), phase=15)):
    add(f"turntable_screw_{k + 1:02d}", s, 1, SCREW, part_number="ISO4762-M10x35")

low = rrect(Plane.XY.offset(TT_TOP - 1), 40, 0, 230, 250, 100).wire()
mid = rrect(Plane.XY.offset(SZ - 150), SX - 10, 0, 250, 230, 60).wire()
top = rrect(Plane.XY.offset(SZ), SX, 0, 230, 210, 40).wire()
shoulder = fuse_all(
    [
        loft([low, mid, top]),
        ycyl(150, -130, 92, SX, SZ),
        make_cylinder(52, 30, (-118, 0, TT_TOP - 2)),
    ]
)
shoulder = soft_fillet(
    shoulder,
    10,
    [
        e
        for e in edges(shoulder)
        if abs(bounding_box(e)[0][1] - bounding_box(e)[1][1]) < 1e-6
        and bounding_box(e)[0][1] in (-130.0, 92.0)
    ],
)
add("shoulder_housing", shoulder, 1, CAST, part_number="RB-130-SH", material="EN-GJS-400 painted")
add(
    "j2_gear_cap",
    ycyl(128, -152, -128, SX, SZ),
    1,
    ACCENT,
    part_number="RB-131-GC",
    material="AlSi10Mg painted",
)
for k, s in enumerate(screw_ring(10, 10, 2 * 112, "-y", (SX, -152, SZ), phase=18)):
    add(f"j2_cap_screw_{k + 1:02d}", s, 1, SCREW, part_number="ISO4762-M10x30")
add_servo("j2_servo", MOTOR_R, 230, "-y", (SX, -151, SZ), 1, spin=90, rating="2.5 kW")
add_servo(
    "j1_servo", 0.8 * MOTOR_R, 190, "+z", (-118, 0, TT_TOP + 27), 1, spin=180, rating="2.0 kW"
)
harness(
    "harness_shoulder",
    0.0,
    [(-118, TT_TOP + 245), (-118, SZ + 40), (-30, SZ + 110), (30, SZ + 60)],
    45,
    1,
    [(1, 0.5)],
)

# ================================================================ 2  upper arm (J2)
ay0, ay1 = ARM_Y - ARM_T / 2, ARM_Y + ARM_T / 2
arm = loft(
    [
        rrect(Plane.XY.offset(SZ), SX, ARM_Y, 240, ARM_T, 30).wire(),
        rrect(Plane.XY.offset(J3Z), SX, ARM_Y, 165, ARM_T, 30).wire(),
    ]
)
arm = fuse_all([arm, ycyl(140, ay0, ay1, SX, SZ), ycyl(102, ay0, ay1, SX, J3Z)])
pockets = []
face_plane = Plane((0, ay1 + 1, 0), (0, -1, 0), (1, 0, 0))


def hw(z):
    """Half the width of a rib pocket at height z: the arm's taper less the wall."""
    return (240 - 75 * (z - SZ) / UPPER_ARM) / 2 - 24


c = 16
for z0, z1 in ((SZ + 165, SZ + 300), (SZ + 320, SZ + 445), (SZ + 465, J3Z - 125)):
    pockets.append(
        extrude(
            polygon_face(
                [
                    (SX - hw(z0) + c, z0),
                    (SX + hw(z0) - c, z0),
                    (SX + hw(z0), z0 + c),
                    (SX + hw(z1), z1 - c),
                    (SX + hw(z1) - c, z1),
                    (SX - hw(z1) + c, z1),
                    (SX - hw(z1), z1 - c),
                    (SX - hw(z0), z0 + c),
                ],
                face_plane,
            ),
            40,
            (0, -1, 0),
        )
    )
arm = cut_all(arm, pockets)
add("upper_arm", arm, 2, CAST, part_number="RB-140-UA", material="EN-GJS-400 painted, ribbed")
add(
    "j2_arm_cap",
    ycyl(112, ay1 - 1, ay1 + 14, SX, SZ),
    2,
    ACCENT,
    part_number="RB-141-AC",
    material="AlSi10Mg painted",
)
for k, s in enumerate(screw_ring(8, 8, 2 * 96, "+y", (SX, ay1 + 14, SZ), phase=22.5)):
    add(f"j2_arm_cap_screw_{k + 1}", s, 2, SCREW, part_number="ISO4762-M8x25")
add(
    "j3_reducer",
    fuse(ycyl(96, ay1 - 1, ay1 + 26, SX, J3Z), ycyl(84, ay1 + 25, ay1 + 34, SX, J3Z)),
    2,
    ACCENT,
    part_number="RB-142-RD",
    material="AlSi10Mg painted",
)
for k, s in enumerate(screw_ring(8, 8, 2 * 89, "+y", (SX, ay1 + 26, J3Z), phase=22.5)):
    add(f"j3_reducer_screw_{k + 1}", s, 2, SCREW, part_number="ISO4762-M8x30")
add_servo("j3_servo", 0.85 * MOTOR_R, 200, "+y", (SX, ay1 + 33, J3Z), 2, spin=0, rating="1.8 kW")
harness(
    "harness_upper_arm",
    ARM_Y,
    [(SX - 105, SZ + 40), (SX - 190, SZ + 160), (SX - 165, J3Z - 170), (SX - 70, J3Z - 50)],
    70,
    2,
    [(1, 0.25), (1, 0.75)],
)

# ================================================================ 3  elbow and forearm housing (J3)
fy = 92.0
rear = extrude(
    rrect(
        Plane((0, -fy, 0), (0, -1, 0), (1, 0, 0)),
        SX - 15,
        (J3Z + J4Z) / 2 + 5,
        310,
        FOREARM_RISE + 175,
        55,
    ).face(),
    2 * fy,
    (0, 1, 0),
)
elbow = fuse_all(
    [rear, ycyl(112, -fy - 6, ay0 - 2, SX, J3Z), xcyl(100, SX - 175, SX + 240, 0, J4Z)]
)
elbow = soft_fillet(
    elbow,
    8,
    [
        e
        for e in edges(elbow)
        if abs(bounding_box(e)[0][1] - bounding_box(e)[1][1]) < 1e-6
        and abs(abs(bounding_box(e)[0][1]) - fy) < 1e-6
    ],
)
add("elbow_housing", elbow, 3, CAST, part_number="RB-150-EH", material="EN-GJS-400 painted")
add(
    "elbow_cover",
    ycyl(96, -fy - 18, -fy - 5, SX, J3Z),
    3,
    ACCENT,
    part_number="RB-151-EC",
    material="AlSi10Mg painted",
)
for k, s in enumerate(screw_ring(8, 8, 2 * 82, "-y", (SX, -fy - 18, J3Z), phase=22.5)):
    add(f"elbow_cover_screw_{k + 1}", s, 3, SCREW, part_number="ISO4762-M8x25")
add_servo("j4_servo", 0.75 * MOTOR_R, 180, "-x", (SX - 174, 0, J4Z), 3, spin=-90, rating="0.9 kW")

# ============================================================== 4  forearm tube and wrist yoke (J4)
x0, x1 = SX + 255, J5X - 130


def sec(x, w, h, r):
    return rrect(Plane((x, 0, 0), (1, 0, 0), (0, 1, 0)), 0, J4Z, w, h, r).wire()


tube = loft([sec(x0 - 2, 170, 180, 70), sec(x1, 120, 130, 50)])
yoke = [make_box(60, 150, 116, (J5X - 150, -75, J4Z - 58))]
for s in (-1, 1):
    yy = (52, 74) if s > 0 else (-74, -52)
    yoke += [make_box(140, 22, 104, (J5X - 140, yy[0], J4Z - 52)), ycyl(52, yy[0], yy[1], J5X, J4Z)]
forearm = fuse_all([tube] + yoke)
add("forearm", forearm, 4, CAST, part_number="RB-160-FA", material="AlSi10Mg casting, painted")
ring = cut(xcyl(103, SX + 238, SX + 258, 0, J4Z), xcyl(60, SX + 237, SX + 259, 0, J4Z))
add("j4_bearing_ring", ring, 4, MACHINED, part_number="RB-161-BR", material="42CrMo4")
add(
    "forearm_band",
    cut(xcyl(84, SX + 380, SX + 420, 0, J4Z), xcyl(40, SX + 379, SX + 421, 0, J4Z)),
    4,
    ACCENT,
    part_number="RB-162-BD",
    material="painted steel band",
)
for s, d in ((1, "+y"), (-1, "-y")):
    cap_y = 74 * s
    add(
        f"j5_bearing_cap_{'right' if s > 0 else 'left'}",
        ycyl(
            44,
            min(cap_y, cap_y + 8 * s) - (1 if s > 0 else 0),
            max(cap_y, cap_y + 8 * s) + (0 if s > 0 else 1),
            J5X,
            J4Z,
        ),
        4,
        MACHINED,
        part_number="RB-163-BC",
        material="7075-T6 anodised",
    )
    for k, sc in enumerate(screw_ring(6, 6, 2 * 34, d, (J5X, cap_y + 8 * s, J4Z), phase=30)):
        add(
            f"j5_cap_screw_{'r' if s > 0 else 'l'}{k + 1}",
            sc,
            4,
            SCREW,
            part_number="ISO4762-M6x20",
        )

# ================================================================ 5  wrist body (J5)
wrist = fuse_all([ycyl(46, -51, 51, J5X, J4Z), xcyl(42, J5X, FLANGE_X - 12, 0, J4Z)])
add("wrist_body", wrist, 5, CAST, part_number="RB-170-WB", material="AlSi10Mg painted")
add(
    "j6_seal_ring",
    cut(
        xcyl(40, FLANGE_X - 13, FLANGE_X - 9, 0, J4Z), xcyl(30, FLANGE_X - 14, FLANGE_X - 8, 0, J4Z)
    ),
    5,
    MACHINED,
    part_number="RB-171-SR",
)

# ================================================================ 6  tool flange and gripper (J6)
fl = xcyl(FLANGE_D / 2, FLANGE_X - 10, FLANGE_X, 0, J4Z)
fl = cut_all(
    fl,
    [
        xcyl(
            3.3,
            FLANGE_X - 10,
            FLANGE_X,
            FLANGE_PCD / 2 * math.cos(math.radians(45 + 90 * k)),
            J4Z + FLANGE_PCD / 2 * math.sin(math.radians(45 + 90 * k)),
        )
        for k in range(4)
    ]
    + [
        xcyl(3, FLANGE_X - 6, FLANGE_X, FLANGE_PCD / 2, J4Z),
        xcyl(15.75, FLANGE_X - 6, FLANGE_X, 0, J4Z),
    ],
)
add("tool_flange", fl, 6, MACHINED, part_number="ISO9409-1-50-4-M6", material="42CrMo4, ground")
ad_t = 12
adapter = fuse(
    xcyl(40, FLANGE_X, FLANGE_X + ad_t, 0, J4Z), xcyl(15.5, FLANGE_X - 5, FLANGE_X + 1, 0, J4Z)
)
add("gripper_adapter", adapter, 6, MACHINED, part_number="GRP-ADP-50", material="6082-T6 anodised")
for k, s in enumerate(screw_ring(6, 4, FLANGE_PCD, "+x", (FLANGE_X + ad_t, 0, J4Z), phase=45)):
    add(f"adapter_screw_{k + 1}", s, 6, SCREW, part_number="ISO4762-M6x20")
gx = FLANGE_X + ad_t
body = make_box(75, 150, 84, (gx, -75, J4Z - 42))
body = soft_fillet(body, 8, edges_parallel_to(body, (1, 0, 0)))
body = cut(body, make_box(30, 152, 20, (gx + 46, -76, J4Z - 10)))  # jaw guide slot
add("gripper_body", body, 6, GRIPPER, part_number="GRP-PG-80", material="7075-T6, black anodised")
for k, y in enumerate((-40.0, 40.0)):
    fit = fuse(
        make_cylinder(6, 14, (gx + 20, y, J4Z + 41)),
        translate(hexagon(14, 6), (gx + 20, y, J4Z + 48)),
    )
    add(f"air_fitting_{k + 1}", fit, 6, MACHINED, part_number="FIT-G18-6")
for s, side in ((1, "right"), (-1, "left")):
    inner = GRIP_OPEN / 2 + 6
    jaw_y = (inner, inner + 34) if s > 0 else (-inner - 34, -inner)
    jaw = make_box(36, 34, 70, (gx + 44, jaw_y[0], J4Z - 35))
    add(
        f"jaw_{side}",
        soft_fillet(jaw, 3, edges_parallel_to(jaw, (0, 1, 0))),
        6,
        MACHINED,
        part_number="GRP-JAW",
        material="7075-T6 anodised",
    )
    fy0 = inner if s > 0 else -inner - 16
    finger = extrude(
        polygon_face(
            [
                (gx + 78, J4Z - 30),
                (gx + 78 + FINGER_LEN - 25, J4Z - 30),
                (gx + 78 + FINGER_LEN, J4Z - 16),
                (gx + 78 + FINGER_LEN, J4Z + 16),
                (gx + 78 + FINGER_LEN - 25, J4Z + 30),
                (gx + 78, J4Z + 30),
            ],
            Plane((0, fy0, 0), (0, -1, 0), (1, 0, 0)),
        ),
        16,
        (0, 1, 0),
    )
    add(f"finger_{side}", finger, 6, MACHINED, part_number="GRP-FNG-105", material="6082-T6")
    pad_y = (GRIP_OPEN / 2, inner + 0.5) if s > 0 else (-inner - 0.5, -GRIP_OPEN / 2)
    pad = make_box(46, pad_y[1] - pad_y[0], 44, (gx + 78 + FINGER_LEN - 54, pad_y[0], J4Z - 22))
    pad = cut(
        pad,
        rotate(
            make_box(
                7, 7, 50, (gx + 78 + FINGER_LEN - 31 - 3.5, s * GRIP_OPEN / 2 - 3.5, J4Z - 25)
            ),
            (gx + 78 + FINGER_LEN - 31, s * GRIP_OPEN / 2, 0),
            (0, 0, 1),
            45,
        ),
    )
    add(f"finger_pad_{side}", pad, 6, ACCENT, part_number="GRP-PAD-V", material="PU 90 Shore A")
    for k, xx in enumerate((gx + 52, gx + 70)):
        add(
            f"finger_screw_{side}_{k + 1}",
            put(
                cap_screw(5),
                "+y" if s > 0 else "-y",
                (xx, jaw_y[1] if s > 0 else jaw_y[0], J4Z + 18),
            ),
            6,
            SCREW,
            part_number="ISO4762-M5x16",
        )
wx = gx + 78 + FINGER_LEN - 31
work = fuse_all(
    [
        make_cylinder(GRIP_OPEN / 2, 70, (wx, 0, J4Z - 35)),
        make_cylinder(GRIP_OPEN / 2 + 12, 22, (wx, 0, J4Z + 35)),
        make_cylinder(GRIP_OPEN / 2 - 8, 26, (wx, 0, J4Z + 56)),
    ]
)
work = cut(work, make_cylinder(9, 140, (wx, 0, J4Z - 40)))
add("workpiece", work, 6, WORKPIECE, part_number="WP-2207", material="CuZn39Pb3 brass, turned")
