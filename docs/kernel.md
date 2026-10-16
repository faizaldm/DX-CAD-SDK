# The model language

A model.py imports nothing. DX-CAD runs it with every name below already in
scope, so a model is a short file of arithmetic and calls, and the first thing
to know about it is what those names are. This page is that list, and it is
written from `dxcad.model.__all__` itself: the test suite compares every row
against the module, signature for signature, so a name that changes here
changes the page or breaks the build.

A model that wants an editor's help can say

```python
from dxcad.model import *
```

as its first line. That line is optional and changes nothing about how the
model runs; it only tells the editor where the names come from.

Shapes are OpenCASCADE's own `TopoDS_Shape` and its kinds, distances are
millimetres, angles are degrees, and every function answers a new shape rather
than changing the one it was given. The three worked models at the foot of this
page are each short enough to read whole.

## The primitives

A solid out of numbers, with no sketch in between. Every one of them stands at the origin unless it is given another, and the units are millimetres.

| Name | Signature | What it is |
| --- | --- | --- |
| `make_box` | `(dx: 'float', dy: 'float', dz: 'float', origin: 'tuple[float, float, float]' = (0.0, 0.0, 0.0)) -> 'TopoDS_Solid'` | Axis-aligned box of size dx * dy * dz with its min corner at origin. |
| `make_cylinder` | `(radius: 'float', height: 'float', origin: 'tuple[float, float, float]' = (0.0, 0.0, 0.0)) -> 'TopoDS_Solid'` | Cylinder of the given radius and height, extruded along +Z. |
| `make_cone` | `(bottom_radius: 'float', top_radius: 'float', height: 'float', origin: 'tuple[float, float, float]' = (0.0, 0.0, 0.0)) -> 'TopoDS_Solid'` | Cone or frustum of the given radii and height, along +Z. |
| `make_sphere` | `(radius: 'float', origin: 'tuple[float, float, float]' = (0.0, 0.0, 0.0)) -> 'TopoDS_Solid'` | Sphere of the given radius, centred on origin. |
| `make_torus` | `(major_radius: 'float', minor_radius: 'float', origin: 'tuple[float, float, float]' = (0.0, 0.0, 0.0)) -> 'TopoDS_Solid'` | Torus of the given radii, its ring centred on origin and its axis +Z. |
| `polygon_face` | `(points: 'Sequence[tuple[float, float]]', plane: 'Plane' = Plane(origin=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), x_dir=(1.0, 0.0, -0.0))) -> 'TopoDS_Face'` | Planar face on `plane` bounded by the polygon through `points`. |
| `make_wire` | `(edges: 'Sequence[TopoDS_Edge]') -> 'TopoDS_Wire'` | One wire built from a sequence of edges, whatever order they are given in. |
| `compound` | `(shapes: 'Sequence[TopoDS_Shape]') -> 'TopoDS_Compound'` | One shape holding every shape given, so a pattern can be carried as a unit. |
| `copy` | `(shape: 'TopoDS_Shape') -> 'TopoDS_Shape'` | An independent copy of a shape, sharing no geometry with it. |
| `stock_box` | `(shape: 'TopoDS_Shape', margin: 'float' = 0.0) -> 'TopoDS_Solid'` | The blank `shape` is cut from: its bounding box grown by `margin`, as a solid. |

## The booleans

Two solids into one. Each answers a solid and leaves what it was given alone, and each raises BooleanError when OCCT cannot make one valid solid of them.

| Name | Signature | What it is |
| --- | --- | --- |
| `fuse` | `(a: 'TopoDS_Shape', b: 'TopoDS_Shape') -> 'TopoDS_Solid'` | The union of a and b, with touching coplanar faces merged into one face. |
| `fuse_all` | `(shapes: 'Sequence[TopoDS_Shape]') -> 'TopoDS_Solid'` | The union of every shape given, fused left to right. |
| `cut` | `(a: 'TopoDS_Shape', b: 'TopoDS_Shape') -> 'TopoDS_Solid'` | a with b removed from it. |
| `cut_all` | `(base: 'TopoDS_Shape', tools: 'Sequence[TopoDS_Shape]') -> 'TopoDS_Solid'` | `base` with every tool cut out of it, in the order given. |
| `common` | `(a: 'TopoDS_Shape', b: 'TopoDS_Shape') -> 'TopoDS_Solid'` | The overlap of a and b. |
| `split` | `(shape: 'TopoDS_Shape', plane: 'Plane') -> 'list[TopoDS_Solid]'` | Cut `shape` with `plane` and return the pieces. |

## Extrude, revolve and the other sweeps

A face or a profile into a solid. This is where a sketch becomes a part.

| Name | Signature | What it is |
| --- | --- | --- |
| `extrude` | `(face: 'TopoDS_Shape', height: 'float', direction: 'Vec3' = (0.0, 0.0, 1.0)) -> 'TopoDS_Solid'` | Sweep a face by `height` along `direction` and return the solid. |
| `revolve` | `(face: 'TopoDS_Shape', point: 'Vec3', direction: 'Vec3', angle: 'float' = 360.0) -> 'TopoDS_Solid'` | Sweep a face `angle` degrees about the axis (point, direction). |
| `loft` | `(profiles: 'Sequence[TopoDS_Wire]') -> 'TopoDS_Solid'` | Build one ruled solid through a sequence of closed profiles, in order. |
| `sweep` | `(profile: 'TopoDS_Face', path: 'TopoDS_Wire') -> 'TopoDS_Solid'` | Sweep a face along a wire and return the one solid it encloses. |
| `draft` | `(solid: 'TopoDS_Shape', faces: 'Sequence[TopoDS_Face]', angle: 'float', neutral_plane: 'Plane') -> 'TopoDS_Solid'` | Tilt each named face by `angle` degrees about where it meets a plane. |
| `hollow` | `(solid: 'TopoDS_Shape', thickness: 'float', faces: 'Sequence[TopoDS_Face]') -> 'TopoDS_Solid'` | Shell a solid to a constant wall thickness, leaving `faces` open. |
| `hollow_facing` | `(solid: 'TopoDS_Shape', thickness: 'float', directions: 'Sequence[Vec3]') -> 'TopoDS_Solid'` | hollow, the faces left open named by the way each faces (item 578). |

## The blends

Rounds and flats along an edge. A blend gets one attempt: when OCCT will not build it, FilletError says so rather than quietly giving back what it started with.

| Name | Signature | What it is |
| --- | --- | --- |
| `fillet` | `(solid: 'TopoDS_Shape', radius: 'float', edges: 'Sequence[TopoDS_Edge] \| None' = None) -> 'TopoDS_Solid'` | Round the given edges of a solid with a constant radius. |
| `fillet_all` | `(solid: 'TopoDS_Shape', radius: 'float') -> 'TopoDS_Solid'` | Round every edge of a solid at once, which is what a cast part wants. |
| `chamfer` | `(solid: 'TopoDS_Shape', distance: 'float', edges: 'Sequence[TopoDS_Edge] \| None' = None) -> 'TopoDS_Solid'` | Cut a symmetric flat across the given edges of a solid. |
| `chamfer_all` | `(solid: 'TopoDS_Shape', distance: 'float') -> 'TopoDS_Solid'` | Cut a flat across every edge of a solid at once, as fillet_all rounds them. |
| `blendable_edges` | `(shape: 'TopoDS_Shape') -> 'list[TopoDS_Edge]'` | The edges of a shape a fillet or a chamfer could act on. |

## The drilled features

A hole through a face of a part already built. The centre is given either in the face's own coordinates or as a world point with `world=`, and exactly one of the two. `world=` may also be a list of points, the one feature drilled at every one in a single cut: a perforated sheet is one `hole` call. Every mouth has to lie wholly on the face and no two may overlap, or nothing is cut.

| Name | Signature | What it is |
| --- | --- | --- |
| `hole` | `(solid: 'TopoDS_Shape', face: 'TopoDS_Face', centre: 'Vec2 \| None', radius: 'float', depth: 'float \| None' = None, *, world: 'Vec3 \| None' = None) -> 'TopoDS_Solid'` | Drill a round hole into `solid` through one of its planar faces. |
| `countersink` | `(solid: 'TopoDS_Shape', face: 'TopoDS_Face', centre: 'Vec2 \| None', radius: 'float', head_radius: 'float', depth: 'float \| None' = None, *, world: 'Vec3 \| None' = None) -> 'TopoDS_Solid'` | Drill a hole with the cone a countersunk screw head sits in above it. |
| `counterbore` | `(solid: 'TopoDS_Shape', face: 'TopoDS_Face', centre: 'Vec2 \| None', radius: 'float', head_radius: 'float', head_depth: 'float', depth: 'float \| None' = None, *, world: 'Vec3 \| None' = None) -> 'TopoDS_Solid'` | Drill a hole with the flat-bottomed bore a socket head sits in above it. |
| `drill_centre` | `(plane: 'Plane', centre: 'Vec2 \| None', world: 'Vec3 \| None', what: 'str' = 'a drill') -> 'Vec2'` | Where a drill goes in the face's own coordinates, from whichever centre was given. |

## The patterns

Copies of a shape, spread out. Each answers a list, which `cut_all` and `fuse_all` take as they stand.

| Name | Signature | What it is |
| --- | --- | --- |
| `linear_pattern` | `(shape: 'TopoDS_Shape', step: 'Vec3', count: 'int') -> 'list[TopoDS_Shape]'` | `count` copies of a shape, each one `step` further along than the last. |
| `circular_pattern` | `(shape: 'TopoDS_Shape', point: 'Vec3', direction: 'Vec3', count: 'int', angle: 'float' = 360.0) -> 'list[TopoDS_Shape]'` | `count` copies of a shape, spread about the axis (point, direction). |

## Text

Letters as a solid (item 574), in a TrueType font the system has: fuse them
with a part to raise them, or sink them their whole depth into a face and
cut them to engrave. A font that is not found is refused, naming some that are.

| Name | Signature | What it is |
| --- | --- | --- |
| `text3d` | `(text: 'str', size: 'float', depth: 'float', font: 'str | None' = None, plane: 'Plane' = Plane(origin=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), x_dir=(1.0, 0.0, -0.0)), at: 'Vec2' = (0.0, 0.0), angle: 'float' = 0.0, align: 'str' = 'left') -> 'TopoDS_Shape'` | The letters of `text` as a solid: `size` high at the capitals, `depth` deep. |
| `TEXT_ALIGNS` | `class` | How a line of text may stand against its point: left, centre or right. |

```python
plate = make_box(50, 20, 5)
top = Plane.XY.offset(5)
part("plate", cut(plate, text3d("DX", 10, 1, plane=top.offset(-1), at=(5, 5))))
```

## The transforms

A copy of a shape, moved. The shape given is never changed.

| Name | Signature | What it is |
| --- | --- | --- |
| `translate` | `(shape: 'TopoDS_Shape', vector: 'Vec3') -> 'TopoDS_Shape'` | A copy of shape moved by vector. |
| `rotate` | `(shape: 'TopoDS_Shape', point: 'Vec3', direction: 'Vec3', angle: 'float') -> 'TopoDS_Shape'` | A copy of shape turned `angle` degrees about the axis (point, direction). |
| `scale` | `(shape: 'TopoDS_Shape', factor: 'float', origin: 'Vec3' = (0.0, 0.0, 0.0)) -> 'TopoDS_Shape'` | A copy of shape enlarged about `origin` by `factor`. |
| `explode` | `(shapes: 'Sequence[TopoDS_Shape]', factor: 'float') -> 'list[TopoDS_Shape]'` | Copies of `shapes` moved apart for an exploded view, as explode_offsets says. |
| `explode_offsets` | `(shapes: 'Sequence[TopoDS_Shape]', factor: 'float') -> 'list[Vec3]'` | How far explode moves each of `shapes`, in order, as (x, y, z). |
| `mirror` | `(shape: 'TopoDS_Shape', point: 'Vec3', normal: 'Vec3') -> 'TopoDS_Shape'` | A copy of shape reflected in the plane through `point` with `normal`. |

## The measurements

What a part weighs, where it balances, how big it is and whether it is sound. These are what a test and an agent check a part with.

| Name | Signature | What it is |
| --- | --- | --- |
| `volume` | `(shape: 'TopoDS_Shape') -> 'float'` | Enclosed volume of a solid, in model units cubed. |
| `surface_area` | `(shape: 'TopoDS_Shape') -> 'float'` | Total area of every face of a shape, in model units squared. |
| `size` | `(shape: 'TopoDS_Shape') -> 'float'` | How big a shape is in the one measure its kind has. |
| `distance` | `(a: 'TopoDS_Shape', b: 'TopoDS_Shape') -> 'float'` | The shortest gap between two shapes, in model units. |
| `closest_points` | `(a: 'TopoDS_Shape', b: 'TopoDS_Shape') -> 'tuple[Vec3, Vec3]'` | Where the gap between two shapes is measured: the point on each. |
| `bounding_box` | `(shape: 'TopoDS_Shape') -> 'tuple[Vec3, Vec3]'` | Axis-aligned extents of a shape as ((xmin, ymin, zmin), (xmax, ymax, zmax)). |
| `centre_of_mass` | `(shape: 'TopoDS_Shape') -> 'Vec3'` | Where a shape balances: the centroid of its volume, area or length. |
| `inertia` | `(shape: 'TopoDS_Shape') -> 'tuple[float, float, float]'` | The three principal moments of inertia, about the shape's centre of mass. |
| `angle_between` | `(a: 'TopoDS_Face', b: 'TopoDS_Face') -> 'float'` | The angle in degrees between the normals of two planar faces, 0 to 180. |
| `is_valid` | `(shape: 'TopoDS_Shape') -> 'bool'` | Whether OCCT calls a shape sound, from BRepCheck_Analyzer. |
| `face_count` | `(shape: 'TopoDS_Shape') -> 'int'` | Number of faces in a shape. |
| `solid_count` | `(shape: 'TopoDS_Shape') -> 'int'` | Number of solids in a shape. |
| `face_plane` | `(face: 'TopoDS_Face') -> 'tuple[Vec3, Vec3]'` | The (point, normal) of a planar face, with the normal pointing outwards. |
| `overhang_faces` | `(shape: 'TopoDS_Shape', angle: 'float' = 45.0, up: 'Vec3' = (0.0, 0.0, 1.0)) -> 'list[TopoDS_Face]'` | The faces a printer would have to bridge or support, printing along `up`. |
| `min_wall_thickness` | `(shape: 'TopoDS_Shape', samples: 'int' = 8) -> 'tuple[float, Vec3]'` | The thinnest wall of a solid and the point on its surface it was measured from. |

## The sections

Where a plane meets a part: as edges, as faces, as wires, or every so far along.

| Name | Signature | What it is |
| --- | --- | --- |
| `section` | `(shape: 'TopoDS_Shape', plane: 'Plane') -> 'list[TopoDS_Edge]'` | The edges where `plane` cuts `shape`, in explorer order. |
| `cross_section` | `(shape: 'TopoDS_Shape', plane: 'Plane') -> 'list[TopoDS_Face]'` | The planar faces where `plane` meets `shape`, in explorer order. |
| `outline` | `(shape: 'TopoDS_Shape', plane: 'Plane') -> 'list[TopoDS_Wire]'` | The section of `shape` at `plane`, as wires rather than loose edges. |
| `slices` | `(shape: 'TopoDS_Shape', plane: 'Plane', step: 'float') -> 'list[tuple[float, list[TopoDS_Face]]]'` | The cross-sections at `plane` and at every `step` along its normal. |

## The explorers

The faces, edges and the rest of a part, in OCCT's own order, which is the order a model can rely on from one run to the next.

| Name | Signature | What it is |
| --- | --- | --- |
| `faces` | `(shape: 'TopoDS_Shape') -> 'list[TopoDS_Face]'` | Every distinct face of a shape, in explorer order. |
| `edges` | `(shape: 'TopoDS_Shape') -> 'list[TopoDS_Edge]'` | Every distinct edge of a shape, in explorer order. |
| `vertices` | `(shape: 'TopoDS_Shape') -> 'list[TopoDS_Vertex]'` | Every distinct vertex of a shape, in explorer order. |
| `wires` | `(shape: 'TopoDS_Shape') -> 'list[TopoDS_Wire]'` | Every distinct wire of a shape, in explorer order. |
| `solids` | `(shape: 'TopoDS_Shape') -> 'list[TopoDS_Solid]'` | Every distinct solid of a shape, in explorer order. |
| `faces_parallel_to` | `(shape: 'TopoDS_Shape', direction: 'Vec3', tolerance: 'float' = 1e-12) -> 'list[TopoDS_Face]'` | The planar faces of a shape whose outward normal points along `direction`. |
| `outermost_face` | `(shape: 'TopoDS_Shape', direction: 'Vec3') -> 'TopoDS_Face'` | The planar face of a shape facing `direction` that lies furthest along it. |
| `edges_parallel_to` | `(shape: 'TopoDS_Shape', direction: 'Vec3', tol: 'float' = 1e-07) -> 'list[TopoDS_Edge]'` | The straight edges of a shape whose line runs parallel to `direction`. |

## Sketches and planes

A profile drawn on a plane, and the planes to draw it on. `Plane.XY`, `Plane.XZ` and `Plane.YZ` are the three standard ones, `Plane.XY.offset(z)` is XY lifted by `z`, and `Plane.from_face(face)` is the plane of a face of a part already built.

| Name | Signature | What it is |
| --- | --- | --- |
| `Sketch` | `(plane: 'Plane' = Plane(origin=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), x_dir=(1.0, 0.0, -0.0))) -> 'None'` | A profile being drawn on a plane. |
| `constrained` | `(plane: 'Plane', points: 'list[Vec2]', constraints: 'list[Horizontal \| Vertical \| Coincident \| Distance \| Radius \| Diameter \| Tangent \| Touch \| Concentric \| Equal]', circles: 'list[tuple[Vec2, Vec2]]' = (), arcs: 'dict[int, Vec2] \| None' = None) -> 'Sketch'` | A closed loop through points named "0", "1" and on, its arcs given by segment number and a point midway along each with centres named "a1" and on, and circles whose centre and rim points are named "c0" and "r0" and on, moved until the constraints all hold. |
| `Horizontal` | `(a: 'str', b: 'str') -> None` | Points a and b at the same y, for `constrained`. |
| `Vertical` | `(a: 'str', b: 'str') -> None` | Points a and b at the same x, for `constrained`. |
| `Coincident` | `(a: 'str', b: 'str') -> None` | Points a and b at the same place, for `constrained`. |
| `Distance` | `(a: 'str', b: 'str', value: 'float') -> None` | Points a and b `value` apart, for `constrained`. |
| `Radius` | `(a: 'str', b: 'str', value: 'float') -> None` | The circle of centre a through rim point b has radius `value`, for `constrained`. |
| `Diameter` | `(a: 'str', b: 'str', value: 'float') -> None` | The circle of centre a through rim point b is `value` across, for `constrained`. |
| `Tangent` | `(a: 'str', b: 'str', c: 'str', d: 'str') -> None` | The line through a and b touches the circle of centre c through rim point d, for `constrained`. |
| `Concentric` | `(a: 'str', b: 'str') -> None` | Two circles, of centres a and b, share their centre, for `constrained`. |
| `Equal` | `(a: 'str', b: 'str', c: 'str', d: 'str') -> None` | Points a and b as far apart as c and d: two sides, or two circles' radii, for `constrained`. |
| `Touch` | `(a: 'str', b: 'str', c: 'str', d: 'str', inside: 'bool' = False) -> None` | The circle of centre a through b touches the circle of centre c through d, outside each other or, with inside, one within the other, for `constrained`. |
| `Plane` | `(origin: 'Vec3', normal: 'Vec3', x_dir: 'Vec3') -> 'None'` | A 2D coordinate system living somewhere in 3D, on top of gp_Ax3. |
| `PlaneHit` | `(point: ForwardRef('Vec3'), uv: ForwardRef('Vec2'), distance: ForwardRef('float'))` | Where a ray met a plane: the world point, its (x, y) and how far along. |
| `Vec2` | `(*args, **kwargs)` | A point on a plane, as (x, y). |
| `Vec3` | `(*args, **kwargs)` | A point or a direction in space, as (x, y, z). |
| `checked_linetype` | `(linetype: 'object') -> 'str'` | `linetype` as one of LINETYPES, any case; ValueError naming them otherwise. |

Every call that finishes a figure, `close`, `end`, `rectangle`,
`rounded_rectangle`, `circle`, `polygon`, `slot`, `ellipse`, `ellipse_arc` and
`spline_piece`, takes `linetype=`, one of `LINETYPES` (item 573). It is how the
figure is drawn and exported, in the sketch's DXF and SVG, and never what an
extrude or a revolve builds:

```python
outline = Sketch(Plane.XY).rectangle((0, 0), (60, 40)).circle((30, 20), 8, linetype="dashed")
part("plate", outline.extrude(5))
```

## Sheet metal

A part of one sheet, bent on its edges, that remembers what it was built from so its flat pattern can be worked out. `part` takes one as it takes a shape and registers its solid.

| Name | Signature | What it is |
| --- | --- | --- |
| `SheetSpec` | `(thickness: 'float', bend_radius: 'float', k_factor: 'float', material: 'str' = 'mild steel') -> None` | The sheet: its thickness, the inside bend radius, the K-factor and its metal, mild steel unless another of the material list's is named. |
| `sheet_part` | `(kind: 'str', *args: 'object', **kwargs: 'object') -> 'SheetPart'` | A plugin's kind of sheet part (item 604), `kind` being `"PLUGIN.NAME"`: the plugin's builder is called with the rest, and the part it answers unfolds through the plugin, by the same flat pipeline as a flanged part. A kind whose plugin is not installed raises ValueError naming the plugin. See [plugins.md](plugins.md). |
| `din_k_factor` | `(bend_radius: 'float', thickness: 'float') -> 'float'` | The K-factor DIN 6935 gives a bend of that inside radius in that sheet: k = 0.65 + 0.5 log10(bend_radius / thickness) for a ratio up to 5 and 1 above it, halved and kept to 0 to 0.5, so a model can say `SheetSpec(2, 2, din_k_factor(2, 2))`. A bend radius or thickness not above 0 raises ValueError. |
| `base_flange` | `(points: 'Sequence[Sequence[float]] | Sketch', spec: 'SheetSpec', plane: 'Plane' = Plane(origin=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), x_dir=(1.0, 0.0, -0.0)), holes: 'Sequence[Sequence[float]]' = (), cutouts: 'Sequence[Sequence[float]]' = (), corner_treatment: 'str | None' = None, corner_gap: 'float | None' = None) -> 'SheetPart'` | A closed profile on a plane, a sheet's thickness thick (its corners, or a `Sketch` of one closed outline of lines and arcs, a whole circle among them), with each `holes` (x, y, diameter) and each `cutouts` (x, y, width, height) rectangle cut through it. `corner_treatment` and `corner_gap` are the part's own for every corner where two returns meet that a flange gives none for. |
| `flange` | `(part: 'SheetPart', edge: 'int | tuple[int, str]', length: 'float', angle: 'float' = 90.0, direction: 'str' = 'up', start_inset: 'float' = 0.0, end_inset: 'float' = 0.0, relief: 'bool' = False, bend_radius: 'float | None' = None, holes: 'Sequence[Sequence[float]]' = (), return_length: 'float' = 0.0, cutouts: 'Sequence[Sequence[float]]' = (), length_from: 'str' = 'leg', corner_treatment: 'str | dict | None' = None, corner_gap: 'float | None' = None, return_angle: 'float' = 90.0, return_direction: 'str' = 'same', hem: 'str | None' = None, teardrop_radius: 'float | None' = None) -> 'SheetPart'` | A new sheet part with a flange bent on profile edge `edge`, or on an edge of the flange already on profile edge n: `(n, "start")` and `(n, "end")`, the ends of its leg, and `(n, "free")`, the free edge of its return, or of its leg when it has none, where `"up"` turns towards the inside face of what the flange stands on, `relief` is refused, and a corner treatment shapes it and a flange it meets in one plane, as [sheetmetal.md](sheetmetal.md) says with the corner post; spanning the edge less `start_inset` and `end_inset`; with `relief`, a slot the thickness wide and bend radius plus thickness deep is cut into the base beside each inset end, and a model.py line says `relief=True`. A `bend_radius` bends this flange alone with that inside radius, the spec's when None, and its flat pattern works the allowance and relief from it; the window's Flange and the `sheet_flange` tool take it, and a model.py line says `bend_radius=` only when it differs from the sheet's. A flange at `angle` 180 is an open hem, its leg back over (or under) the base; a hem with a bend radius of 0, or on an edge sharing a corner with another flange, raises ValueError. `hem` makes it a hem by name: `"closed"`, the leg folded flat onto the base with no bend radius, or `"teardrop"`, the bend turned past 180 degrees round `teardrop_radius`, the flange's bend radius when None, until the leg's free edge comes down to the base; each unfolds by the sheet's K-factor over the angle it turns, takes no return, and is written into a model.py line as `hem=`. Each of `holes`, a (u, v, diameter) with u along the edge from its start and v along the leg from the bend, is cut through the leg and lies on the flat after the base's holes; the `sheet_flange` tool takes them, and a model.py line says `holes=[(u, v, d), ...]` only when there are any. Each of `cutouts`, a (u, v, width, height) rectangle centred at (u, v), width along the edge and height along the leg, is cut through the leg with its holes and lies on the flat as its four corners; the `sheet_flange` tool takes them, and a model.py line says `cutouts=[(u, v, w, h), ...]` after any holes only when there are any. A `return_length` above 0 makes a return flange: a second 90 degree bend at the leg's end, turning the same way, then a return leg that long, as a channel's lip; only a 90 degree flange takes one, and its flat has a second bend; `return_angle`, above 0 and below 180, and `return_direction`, `"same"` to turn it in over the base or `"opposite"` to turn it out away from it, bend the return its own way, when no corner treatment shapes it and its free edge takes no flange; the window's Flange and the `sheet_flange` tool take it, and a model.py line says `return_length=` only when it is above 0. With `length_from` `"outside"`, `length` runs to the outside mould line, so the straight leg is `length` less `outside_setback()` at the flange's radius, refused on a hem and when it leaves no leg; the part keeps the leg, and the `sheet_flange` tool takes it, and a model.py line says `length_from=` only when it is not `"leg"`. Where its return meets another's at a corner, `corner_treatment` (`"mitre"`, `"square"`, `"open"` or `"none"`, or a dict of them by corner) shapes the two with `corner_gap` between them, the part's own or mitre (said in its notes) when not given; a flange that would overlap the part anywhere raises ValueError naming the overlap's size and place. |
| `flat_pattern` | `(part: 'SheetPart') -> 'FlatPattern'` | The sheet part unfolded: its cut outline, its bends, its holes and its cutouts, on the base's plane. |
| `flat_solid` | `(pattern: 'FlatPattern') -> 'TopoDS_Solid'` | The flat pattern as a solid: the outline extruded by the thickness from z = 0 on XY, every hole and cutout cut through it. `part` registers it as any shape; a part made from the flat of a sheet part the model registers too is that part's flat, listed under it and counted once with it in a bill, a parts list and a mass. |
| `Bend` | `(lines: 'tuple[Segment, Segment]', angle: 'float', direction: 'str', radius: 'float') -> None` | One bend as it lies on a flat: its two bend lines, where it starts and ends, its angle, its direction (`"up"` or `"down"`) and its inside radius. |
| `FlatPattern` | `(outline: 'tuple[Vec2, ...]', bends: 'tuple[Bend, ...]', spec: 'SheetSpec', holes: 'tuple[Hole, ...]' = (), cutouts: 'tuple[Cutout, ...]' = (), leg_cutouts: 'tuple[tuple[Vec2, Vec2, Vec2, Vec2], ...]' = (), notes: 'tuple[tuple[float, float, str] | tuple[float, float, str, float], ...]' = (), cuts: 'tuple[tuple[Vec2, ...], ...]' = (), openings: 'tuple[tuple[Vec2, ...], ...]' = (), arcs: 'tuple[FlatArc, ...]' = ()) -> None` | A sheet part unfolded, as `flat_pattern` answers it: the closed outline, the bends, the holes (x, y, diameter), the cutouts (x, y, width, height) and the flanges' cutouts by their four corners, on the base's plane, with any notes (x, y, text), or (x, y, text, height) at a height of their own, a plugin writes on the NOTES layer, any open cut lines, which are cut and counted in the cut length but not the area, and any openings of any shape inside the outline, closed polygons cut through it and taken off the area. A plugin's unfold builds one; see [plugins.md](plugins.md). |
| `SheetPart` | `(solid: 'TopoDS_Solid', spec: 'SheetSpec', profile: 'tuple[Vec2, ...]', plane: 'Plane', flanges: 'tuple[Flange, ...]' = (), holes: 'tuple[Hole, ...]' = (), flange_holes: 'tuple[FlangeHole, ...]' = (), cutouts: 'tuple[Cutout, ...]' = (), flange_cutouts: 'tuple[FlangeCutout, ...]' = (), return_holes: 'tuple[FlangeHole, ...]' = (), return_cutouts: 'tuple[FlangeCutout, ...]' = (), corner_trims: 'tuple[tuple[int, tuple[Vec2, ...]], ...]' = (), corner_cuts: 'tuple[tuple[FlangeEdge, str, tuple[Vec2, ...]], ...]' = (), corner_tabs: 'tuple[tuple[FlangeEdge, str, tuple[Vec2, ...]], ...]' = (), return_turns: 'tuple[tuple[FlangeEdge, float, str], ...]' = (), corner_treatment: 'str | None' = None, corner_gap: 'float | None' = None, notes: 'tuple[str, ...]' = (), arcs: 'tuple[ProfileArc, ...]' = (), kind: 'str | None' = None, record: 'object' = None) -> None` | A sheet part: its solid and the record it was built from, as `base_flange`, `flange` and a plugin's builder answer it. A flange on a flange's edge is in `flanges` under its `(n, where)`, and `corner_cuts` and `corner_tabs` are what the corner treatments took off and added where it meets another in one plane. `return_turns` names each return that is not a quarter turn the same way, with its angle and `"same"` or `"opposite"`. A plugin's builder keeps what its unfold needs in `record`; see [plugins.md](plugins.md). |

```python
spec = SheetSpec(2, 2, 0.44)
tray = base_flange([(0, 0), (100, 0), (100, 50), (0, 50)], spec)
tray = flange(tray, 1, 20)
part("tray", tray)
part("tray_flat", flat_solid(flat_pattern(tray)))
```

## The readers

A shape read off the disk. A relative path is taken from the directory the model is in.

| Name | Signature | What it is |
| --- | --- | --- |
| `import_step` | `(path: 'str \| _os.PathLike[str]') -> '_Shape'` | Read a STEP file back into one shape. |
| `import_brep` | `(path: 'str \| _os.PathLike[str]') -> '_Shape'` | Read a BREP file back into one shape. |

## part

The one name a model must call, or `place`, which calls it. Everything else builds shapes; this is what makes one an entry of the project, under the name it will be known by.

| Name | Signature | What it is |
| --- | --- | --- |
| `part` | `(name: 'str', shape: '_Shape', color: 'str | None' = None, part_number: 'str | None' = None, revision: 'str | None' = None, properties: 'dict[str, str] | None' = None) -> '_Shape'` | Register `shape` as the project entry `name` and give it back. |
| `place` | `(name: 'str', source, at=(0.0, 0.0, 0.0), rotate=(0.0, 0.0, 0.0), part=None) -> '_Shape'` | Put `source` in as the part `name`, turned by `rotate` and moved to `at`. |
| `use` | `(path, part: 'str | None' = None, as_group: 'bool' = False)` | The parts another part or assembly file's model builds, by name, or the one named (item 576). |
| `mate` | `(part: 'str', ref: 'str', to: 'str', to_ref: 'str', kind: 'str', value=None) -> '_Shape'` | Place part `part` against part `to` by one mate (item 575), and give it back placed. |
| `identity` | `(name: 'str', part_number: 'str | None' = None, revision: 'str | None' = None, properties: 'dict[str, str] | None' = None) -> 'None'` | Give part `name`, registered already, its part number, revision and properties (item 697), however it was made: in a loop, by a helper or on its own `part()` line. A later `identity()` for the same part takes its place, and a `part()` line's own `part_number=`, `revision=` or `properties=` win over it. The Parts dock writes one after the parts when a part number is set. A name that is not a part yet raises ValueError. |
| `rename` | `(old: 'str', new: 'str') -> 'None'` | Give part `old`, registered already, the name `new` (item 711), where it stands: its colour, identity, mates and place in the parts list go with it, and the statements after it name it `new`. The window writes one after the parts when a part made in a loop or a helper is renamed, as such a part has no `part()` line whose name can change; a second rename of the part rewrites it. A name that is not a part yet raises ValueError; a name another part has is refused. |

`place` is how a model is an assembly: one shape, or one part read from a
file, put in as many parts as it is needed, each at its own position. `source`
is a shape the model built, a `.step`, `.stp` or `.brep` file, or a `.dxcprt` or `.dxcasm`
project with `part=` naming one of its parts; a relative path is taken from
the directory the model is in, and a file placed four times is read once.
`rotate` is degrees about X, then Y, then Z, through the shape's own origin,
and `at` is where that origin goes. Each placement is a part of its own, and
`dxcad describe` and the agent door's document tools say where it was put and
what it came from:

```python
bracket = fuse(make_box(40, 20, 4), make_box(4, 20, 30))
place("bracket_left", bracket)
place("bracket_right", bracket, at=(100, 0, 0), rotate=(0, 0, 180))
for number, x in enumerate((10, 30, 70, 90), start=1):
    place(f"bolt_{number}", "bolt.step", at=(x, 10, 4))
```

A part may be given a colour, `color="#RRGGBB"` or one of grey, red, orange,
yellow, green, blue, violet, black and white, or of the Designmatix palette
the examples use: steel, galvanised, navy, dx-red, brass and hardware; any
other is refused, naming them. The colour is kept in the statement, so the
window draws the part in it and STEP, 3MF and `dxcad render` carry it; the
Parts dock's Colour swatch writes it there. A part placed from another
`.dxcprt` with `use()` keeps the colour that file gives it:

```python
part("plate", make_box(40, 30, 5), color="blue")
part("pin", make_cylinder(3, 20), color="#D62728")
```

A part may also carry the identity a shop's systems know it by:
`part_number=` and `revision=`, each one line of text, and `properties=`, a
dict of text by name. They are kept in the statement as a colour is, and the
Parts dock's Part number, Revision and Properties fields write them there.
`dxcad bom`, the Bill of Materials window and a drawing's parts list show the
part number and revision; STEP carries all three (the product's id, its
version's id and its general properties) and 3MF carries them as the object's
metadata:

```python
part("bracket", make_box(40, 30, 5), part_number="BR-100", revision="B",
     properties={"finish": "zinc", "supplier": "Acme"})
```

Item 576: `use(path, part=None)` takes the parts another part or assembly file's model builds,
run in its own scope from that file's folder, as a dict by name, or the one
part named; the path is relative to this model's folder, and what it built is
kept until the file changes. Place, pattern or mate them as any other shape;
a used part placed is counted by its file in `dxcad bom`. A file that is not
there is refused by its path, and one that uses itself, directly or through
another, naming the loop.

Item 577: `use(path, as_group=True)` takes an assembly file's parts as one
sub-assembly, which `place(name, group)` puts in whole, each part as
`name/part` where it sits within it, and which `mate(name, ...)` moves as one
by the faces of its parts. `dxcad bom` lists sub-assemblies as a tree with
their counts multiplied down it, `--flat` totals each part, an exploded view
moves a group as one, and a STEP export nests them as assemblies.

```python
hinge = use("hinge.dxcasm", as_group=True)
place("hinge_top", hinge, at=(0, 40, 1800))
place("hinge_bottom", hinge, at=(0, 40, 100))
```

```python
bracket = use("bracket.dxcprt", "bracket")
place("bracket_1", bracket, at=(0, 0, 4))
place("bracket_2", bracket, at=(80, 0, 4))
place("plate", use("plate.dxcprt")["plate"])
```

Item 575: `mate` places a part against a part placed before it, by faces
and axes rather than numbers, so a mated part follows what it is mated to.
A kind is `coincident` (two faces flush, normals opposed), `concentric` (two
axes in line), `distance` (two faces parallel and opposed, `value` apart) or
`angle` (`value` degrees). A ref is `'>Z'` or `'<X'`, the outermost plane
facing that way, `'<Z 2'` the second one out, `'facing (x, y, z) N'` for any
direction, or `'hole N'` and `'cylinder N'` for an axis. Item 584 settled
three rules for reading them:

- Planes are counted, not faces. Planar faces facing that way whose planes
  lie within the kernel's tolerance (`PLANE_TOLERANCE`) of each other are one
  level, so a top face split by a slot is still `'>Z'`.
- Holes and cylinders are counted by position, not by the kernel's listing
  order. Holes go by their axis's centre, sorted by x, then y, then z, each
  rounded to `1e-6`, as `dxcad describe` lists them. Cylinders go by radius,
  thinnest first, and cylinders of one radius by the same centre order.
- Every ref is read in the part's own frame, as the model built it, before
  its placement or its mates, so a part placed on its side keeps its `'>Z'`.

A ref past the last one is refused listing what there is: `'<Z 3'` on the bolt
below is refused with "2 planes face -Z, at z = 0 and 20". A part's mates are met in the
order given, each within the freedom the ones before it left; one that cannot
be met is refused, naming it and the distance or angle it misses by, and so
is a mate to a part placed after. `dxcad describe` and the Parts dock say what
freedom is left.

```python
plate = cut(make_box(60, 40, 5), translate(make_cylinder(3, 5), (20, 20, 0)))
part("plate", plate)
part("bolt", fuse(make_cylinder(3, 20), translate(make_cylinder(5, 4), (0, 0, 20))))
mate("bolt", "cylinder 1", "plate", "hole 1", "concentric")
mate("bolt", "<Z 2", "plate", ">Z", "coincident")
```

Item 671: mates can be suggested, never added unasked. Model > Suggest
Mates..., with a part picked, lists the mates its features allow against the
parts near it: a cylinder to a hole it fits (up to 15 percent and 0.2 mm
larger) as concentric, opposed faces as coincident, first where a shank
stands out of the part's face and its hole runs into the other's, and the
same faces as distance with the measured gap. Moving a part near another says
on the status bar that mates are suggested. They are ranked by simple counts
of the user's own accepts, kept in the settings and keyed by the features
involved ("concentric 6 mm cylinder to 6.6 mm hole"), then by how well and
how near the features match. Each one the user accepts is written as its own
mate statement, with its own undo entry. The agent door's `suggest_mates`
answers the same list, for an assistant to propose and the user to confirm.
No trained machine-learning model predicts a mate, no parts are clustered by
a signature of their shape, and no mate is ever added automatically (patent
guardrails, US 11,321,605 / EP 3486812).

## The constants

The numbers the kernel judges by, in scope so that a model can be held to the same ones.

| Name | Signature | What it is |
| --- | --- | --- |
| `BOOLEAN_FUZZY_VALUE` | `1e-05` | The fuzzy value a boolean is retried with when the first attempt fails. |
| `DEFAULT_LINETYPE` | `class` | The linetype a sketch figure is drawn in when none is given: `'continuous'`. |
| `EDGE_PARALLEL_TOLERANCE` | `1e-07` | How far off parallel an edge may be and still be counted. |
| `FULL_TURN` | `360.0` | Degrees in a whole turn, which is what revolve and circular_pattern default to. |
| `LINETYPES` | `class` | The linetypes a sketch figure may be drawn in: continuous, dashed, centre and phantom. |
| `LOOP_AREA_TOLERANCE` | `1e-06` | The area below which a sketch loop is taken to be nothing at all. |
| `MINIMUM_SEGMENTS` | `3` | The fewest segments a closed sketch loop can have. |
| `OVERHANG_BED_TOLERANCE` | `1e-06` | How close to the lowest point of a part a face must lie to count as on the bed. |
| `OVERHANG_SAMPLES` | `8` | Samples per side of the UV grid a curved face's normals are read on. |
| `PLANE_PARALLEL_TOLERANCE` | `1e-12` | How far off parallel a face's normal may be and still count. |
| `PLANE_TOLERANCE` | `1e-07` | How far a point may be off a plane and still be taken to be on it. |
| `WALL_RAY_START` | `1e-06` | How far along a ray a hit must be before it counts as the far side of a wall. |

## The errors

What an operation raises when it cannot build one valid solid. A model that means to carry on regardless catches these by name.

| Name | Signature | What it is |
| --- | --- | --- |
| `BooleanError` | `class` | A boolean operation did not produce one valid solid. |
| `DraftError` | `class` | A draft did not produce one valid solid. |
| `FilletError` | `class` | A fillet or chamfer did not produce one valid solid. |
| `HollowError` | `class` | A shelling operation did not produce one valid solid. |
| `LoftError` | `class` | A loft did not produce one valid solid. |
| `SketchError` | `class` | A sketch is not a usable profile: open, too short, or crossing itself. |
| `SweepError` | `class` | A sweep along a path did not produce one valid solid. |

## What OCCT and Python bring with them

These are in scope because `dxcad.kernel` and `dxcad.sketch` import them, not because a model is meant to use them. They are OpenCASCADE's own classes and enumerations and a few of Python's, and nothing here promises them from one version to the next: a model that reaches for one is writing OCCT, not DX-CAD.

| Name | Signature | What it is |
| --- | --- | --- |
| `BRepAdaptor_Curve` | `class` | The Curve from BRepAdaptor allows to use an Edge of the BRep topology like a 3D curve.The Curve from BRepAd... |
| `BRepAdaptor_Surface` | `class` | The Surface from BRepAdaptor allows to use a Face of the BRep topology look like a 3D surface.The Surface f... |
| `BRepAlgoAPI_BooleanOperation` | `class` | The root API class for performing Boolean Operations on arbitrary shapes. |
| `BRepAlgoAPI_Common` | `class` | The class provides Boolean common operation between arguments and tools (Boolean Intersection). |
| `BRepAlgoAPI_Cut` | `class` | The class Cut provides Boolean cut operation between arguments and tools (Boolean Subtraction). |
| `BRepAlgoAPI_Fuse` | `class` | The class provides Boolean fusion operation between arguments and tools (Boolean Union). |
| `BRepAlgoAPI_Section` | `class` | The algorithm is to build a Section operation between arguments and tools. |
| `BRepAlgoAPI_Splitter` | `class` | The class contains API level of the **Splitter** algorithm, which allows splitting a group of arbitrary sha... |
| `BRepBndLib` | `class` | This package provides the bounding boxes for curves and surfaces from BRepAdaptor. |
| `BRepBuilderAPI_Copy` | `class` | Duplication of a shape. |
| `BRepBuilderAPI_MakeEdge` | `class` | Provides methods to build edges. |
| `BRepBuilderAPI_MakeFace` | `class` | Provides methods to build faces. |
| `BRepBuilderAPI_MakePolygon` | `class` | Describes functions to build polygonal wires. |
| `BRepBuilderAPI_MakeWire` | `class` | Describes functions to build wires from edges. |
| `BRepBuilderAPI_Transform` | `class` | Geometric transformation on a shape. |
| `BRepCheck_Analyzer` | `class` | A framework to check the overall validity of a shape. |
| `BRepClass_FaceClassifier` | `class` | Tells whether a point in a face's own (u, v) lies inside it, on its boundary or outside. |
| `BRepExtrema_DistShapeShape` | `class` | This class provides tools to compute minimum distance between two Shapes (Compound,CompSolid, Solid, Shell,... |
| `BRepFilletAPI_MakeChamfer` | `class` | Describes functions to build chamfers on edges of a shell or solid. |
| `BRepFilletAPI_MakeFillet` | `class` | Describes functions to build fillets on the broken edges of a shell or solid. |
| `BRepGProp` | `class` | Provides global functions to compute a shape's global properties for lines, surfaces or volumes, and bring... |
| `BRepOffsetAPI_DraftAngle` | `class` | Taper-adding transformations on a shape. |
| `BRepOffsetAPI_MakePipe` | `class` | Describes functions to build pipes. |
| `BRepOffsetAPI_MakeThickSolid` | `class` | Describes functions to build hollowed solids. |
| `BRepOffsetAPI_ThruSections` | `class` | Describes functions to build a loft. |
| `BRepPrimAPI_MakeBox` | `class` | Describes functions to build parallelepiped boxes. |
| `BRepPrimAPI_MakeCone` | `class` | Describes functions to build cones or portions of cones. |
| `BRepPrimAPI_MakeCylinder` | `class` | Describes functions to build cylinders or portions of cylinders. |
| `BRepPrimAPI_MakePrism` | `class` | Describes functions to build linear swept topologies, called prisms. |
| `BRepPrimAPI_MakeRevol` | `class` | Class to make revolved sweep topologies. |
| `BRepPrimAPI_MakeSphere` | `class` | Describes functions to build spheres or portions of spheres. |
| `BRepPrimAPI_MakeTorus` | `class` | Describes functions to build tori or portions of tori. |
| `BRepTools` | `class` | The BRepTools package provides utilities for BRep data structures. |
| `BRep_Builder` | `class` | A framework providing advanced tolerance control. |
| `BRep_Tool` | `class` | Provides class methods to access to the geometry of BRep shapes. |
| `Bnd_Box` | `class` | Describes a bounding box in 3D space. |
| `GC_MakeArcOfCircle` | `class` | Implements construction algorithms for an arc of circle in 3D space. |
| `GProp_GProps` | `class` | Implements a general mechanism to compute the global properties of a "compound geometric system" in 3d spac... |
| `GeomAbs_Line` | `class` | Identifies the type of a curve. |
| `GeomAbs_Plane` | `class` | Members: |
| `IntCurvesFace_ShapeIntersector` | `class` | Intersects a line with every face of a shape. |
| `NamedTuple` | `(typename, fields=None, /, **kwargs)` | Python's typed namedtuple. |
| `Precision` | `class` | The Precision package offers a set of functions defining precision criteria for use in conventional situati... |
| `Sequence` | `()` | Python's read-only sequence type, used in the signatures above. |
| `ShapeAnalysis_FreeBounds` | `class` | This class is intended to output free bounds of the shape. |
| `ShapeAnalysis_Wire` | `class` | This class provides analysis of a wire to be compliant to CAS.CADE requirements.This class provides analysi... |
| `ShapeFix_Face` | `class` | This operator allows to perform various fixes on face and its wires: fixes provided by ShapeFix_Wire, fixin... |
| `ShapeUpgrade_UnifySameDomain` | `class` | This tool tries to unify faces and edges of the shape which lie on the same geometry. |
| `TopAbs_EDGE` | `class` | Identifies various topological shapes. |
| `TopAbs_FACE` | `class` | Identifies various topological shapes. |
| `TopAbs_IN` | `class` | Identifies the position of a point relative to a region of a shape. |
| `TopAbs_REVERSED` | `class` | Identifies the orientation of a topological shape. |
| `TopAbs_SHELL` | `class` | Identifies various topological shapes. |
| `TopAbs_SOLID` | `class` | Identifies various topological shapes. |
| `TopAbs_ShapeEnum` | `class` | Identifies various topological shapes. |
| `TopAbs_VERTEX` | `class` | Identifies various topological shapes. |
| `TopAbs_WIRE` | `class` | Identifies various topological shapes. |
| `TopExp_Explorer` | `class` | An Explorer is a Tool to visit a Topological Data Structure form the TopoDS package. |
| `TopLoc_Location` | `class` | A Location is a composite transition. |
| `TopTools_HSequenceOfShape` | `class` | OpenCASCADE's own. |
| `TopTools_ListOfShape` | `class` | Purpose: Simple list to link items together keeping the first and the last one. |
| `TopTools_MapOfShape` | `class` | Purpose: Single hashed Map. |
| `TopoDS` | `module` | OpenCASCADE's TopoDS module, which holds the shape classes. |
| `TopoDS_Compound` | `class` | Describes a compound which - references an underlying compound with the potential to be given a location an... |
| `TopoDS_Edge` | `class` | Describes an edge which - references an underlying edge with the potential to be given a location and an or... |
| `TopoDS_Face` | `class` | Describes a face which - references an underlying face with the potential to be given a location and an ori... |
| `TopoDS_Shape` | `class` | Describes a shape which - references an underlying shape with the potential to be given a location and an o... |
| `TopoDS_Solid` | `class` | Describes a solid shape which - references an underlying solid shape with the potential to be given a locat... |
| `TopoDS_Vertex` | `class` | Describes a vertex which - references an underlying vertex with the potential to be given a location and an... |
| `TopoDS_Wire` | `class` | Describes a wire which - references an underlying wire with the potential to be given a location and an ori... |
| `annotations` | `class` | Python's `from __future__ import annotations` switch. |
| `gp_Ax1` | `class` | Describes an axis in 3D space. |
| `gp_Ax2` | `class` | Describes a right-handed coordinate system in 3D space. |
| `gp_Ax3` | `class` | Describes a coordinate system in 3D space. |
| `gp_Dir` | `class` | Describes a unit vector in 3D space. |
| `gp_Lin` | `class` | Describes a line in 3D space. |
| `gp_Pln` | `class` | Describes a plane. |
| `gp_Pnt` | `class` | Defines a 3D cartesian point. |
| `gp_Pnt2d` | `class` | Defines a non-persistent 2D cartesian point. |
| `gp_Trsf` | `class` | Defines a non-persistent transformation in 3D space. |
| `gp_Vec` | `class` | Defines a non-persistent vector in 3D space. |
| `kernel` | `module` | The kernel module itself. |
| `math` | `module` | Python's own math module. |

## Three worked models

Each of these is a whole model.py: copy it into a file, run `dxcad run` over
it, and it builds the one part it names. The volume beside each is what it
builds, and the test suite runs all three and checks them against it, so a
number here is a number DX-CAD answers.

### A box with a hole

The plainest part there is: a primitive, the face to drill through found by
the direction it looks in, and one hole given a world point.

Builds `plate`, 11717.257 cubic millimetres:

```python
LENGTH, WIDTH, THICKNESS = 40.0, 30.0, 10.0
BORE = 6.0

block = make_box(LENGTH, WIDTH, THICKNESS)
top = faces_parallel_to(block, (0, 0, 1))[0]
part("plate", hole(block, top, None, BORE / 2, world=(LENGTH / 2, WIDTH / 2, 0)))
```

The hole is given no depth, so it goes the whole way through, and `None` where
a face-local centre would be says that the centre is the `world` one.

### A revolved bushing

A section drawn on XZ and turned about Z. The section is the wall of the
bushing, from the bore to the outside, and turning it through a whole circle
makes the tube.

Builds `bushing`, 3534.292 cubic millimetres:

```python
OUTER, BORE, HEIGHT = 20.0, 10.0, 15.0

profile = Sketch(Plane.XZ)
profile.rectangle((BORE / 2, 0), (OUTER / 2, HEIGHT))
part("bushing", revolve(profile.face(), (0, 0, 0), (0, 0, 1)))
```

On `Plane.XZ` a sketch's x is the distance from the axis and its y is the
height, which is what a turned part's drawing gives.

### A sketch extruded and filleted

A profile extruded into a pad, and the four upright edges rounded. The edges
are found by the direction they run in rather than by number, so the same two
lines work whatever the pad is.

Builds `pad`, 28542.478 cubic millimetres:

```python
WIDTH, DEPTH, HEIGHT, RADIUS = 60.0, 40.0, 12.0, 5.0

outline = Sketch(Plane.XY)
outline.rectangle((0, 0), (WIDTH, DEPTH))
block = extrude(outline.face(), HEIGHT)
part("pad", fillet(block, RADIUS, edges_parallel_to(block, (0, 0, 1))))
```

A fillet is the one operation with no second attempt: if OCCT will not build
it, `FilletError` is raised and the model stops, which is better than a part
that quietly has no rounds on it.

More models, each doing one thing no other does, are in
[examples/README.md](examples/README.md), and the command that runs them is in
[cli.md](cli.md).
