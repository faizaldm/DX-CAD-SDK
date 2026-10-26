# Sheet metal

A sheet part is one sheet of constant thickness, cut to an outline and bent
up or down along the outline's edges. DX-CAD&trade; builds one from the record a
model.py writes, a base flange and its flanges, and unfolds it from that
same record, so the flat pattern a laser or a plasma table cuts is worked
out from what the part was made of rather than read back out of the solid.
Everything here is in `dxcad.sheetmetal`, and the names a model.py uses are
in scope in every model.py; [kernel.md](kernel.md#sheet-metal) gives their
signatures.

## The sheet

`SheetSpec(thickness, bend_radius, k_factor, material="mild steel")` is
the sheet a part is cut and bent from: its thickness in millimetres, the
inside radius every bend is made with, the K-factor, where the neutral
fibre lies through the thickness, 0 on the inside face and 1 on the
outside, and its metal. The metals are mild steel (7.85 g/cm³), stainless
304 (8.00), aluminium 5052 (2.68) and galvanised steel (7.85), beside the
printing filaments; the window's Parts dock gives a sheet part its own
metal and the mass that follows, where any other part takes the window's
material. A thickness that is not above 0, a negative bend radius, a
K-factor outside 0 to 1 or a material the list has not got is refused, the
last naming the ones it has.

`din_k_factor(bend_radius, thickness)` is the K-factor DIN 6935 gives a
bend of that inside radius in that sheet, for a model that would rather not
pick one: DIN's k = 0.65 + 0.5 x log10(bend radius / thickness) for a ratio
up to 5, and 1 above it, halved and kept to 0 to 0.5. So
`SheetSpec(2, 2, din_k_factor(2, 2))` is a sheet with a K-factor of 0.325.

`SheetSpec.from_gauge(material, thickness)` is the sheet a stocked gauge
makes, from a table per metal: its thickness, a default inside bend radius
and a K-factor. DX-CAD ships the common metric gauges, 0.7, 0.8, 1, 1.2,
1.5, 2, 2.5, 3, 4, 5 and 6 mm, for each of the four metals, each bent at a
radius of one thickness with DIN 6935's K-factor, so
`SheetSpec.from_gauge("mild steel", 2)` is `SheetSpec(2, 2, 0.325)`. A
shop keeps its own table as a CSV with the columns `material`, `thickness`,
`bend_radius` and `k_factor` (left empty for DIN's), at
`%APPDATA%\DX-CAD\gauges.csv` on Windows, `~/Library/Application
Support/DX-CAD/gauges.csv` on a Mac and `~/.config/dxcad/gauges.csv`
elsewhere, or wherever `DXCAD_GAUGES` names; a metal the CSV lists has the
CSV's gauges in place of the shipped ones. A thickness a table has not got
is refused naming the nearest: "mild steel has no 2.2 mm gauge; the nearest
are 2 and 2.5".

## The base flange

`base_flange(points, spec, plane=Plane.XY, holes=(), cutouts=(), corner_treatment=None, corner_gap=None, slots=())` is the
part's start: a closed outline of at least three corners on the plane, the first not
repeated at the end, extruded a thickness along the plane's normal. Edge n
of the outline runs from corner n to corner n + 1, the last closing the
loop; the flanges are put on those edges. `holes` are round holes cut
through the sheet, each an (x, y, diameter) on the plane, each wholly inside
the outline and clear of the others. `cutouts` are rectangles cut through
it, each an (x, y, width, height) centred on (x, y) with its sides along
the plane's axes, each wholly inside the outline and clear of the holes and
the other cutouts; they lie on the flat where they lie on the base.
`slots` are rounded slots cut through it, each an (x1, y1, x2, y2, width):
the centres of its two round ends and its width, as `Sketch.slot(start,
end, width)` draws one, in any direction, not only along x or y. Each lies
wholly inside the outline, clear of the holes, the cutouts and the other
slots; one that does not is refused naming the slot, and so is one whose
two centres are one point, which is a hole. A slot 80 between its ends'
centres and 10 wide takes (80 x 10 + pi x 10² / 4) x the thickness out
of the plate: its length end to end is 90. On the flat it lies where it
lies on the base, and its DXF cuts it as two LINEs and two ARCs on CUT.
`corner_treatment` and `corner_gap` are the part's own, for every corner
where two returns meet that a flange is not given one for (see Corners).

An outline may hold arcs of circles, or be one whole circle: give
`points` as a `Sketch` of one closed outline in place of the corners,
and leave `plane` out, since a sketch is on its own.

```py
disc = base_flange(Sketch(Plane.XY).circle((0, 0), 300), spec)
plate = base_flange(
    Sketch(Plane.XY)
    .move_to((0, 0))
    .line_to((100, 0))
    .arc_via((120, 20), (100, 40))
    .line_to((0, 40))
    .arc_via((-20, 20), (0, 0))
    .close(),
    spec,
)
```

Edge n is still the outline's nth line or arc, and the part keeps which
are arcs. The flat pattern keeps them as arcs: its DXF's outline is an
LWPOLYLINE whose arcs are bulges, its SVG's a path of lines and arcs,
and a disc is one CIRCLE; the cut length and the area are the arcs' own.
A flange is bent on a straight edge only: on an arc `flange` raises
ValueError saying so, `dxcad flat --edges` lists the edge as an arc, and
the Flange dialog lists it greyed. An ellipse or a spline in the outline
is refused. A shop's own flat profile cuts a disc as one circle where it
keeps arcs; any other outline with arcs it writes as the polygon the
arcs are traced as, within 0.01 mm of them.

## Flanges

`flange(part, edge, length, angle=90, direction="up", start_inset=0,
end_inset=0, relief=False, bend_radius=None, holes=(), return_length=0,
cutouts=(), length_from="leg", corner_treatment=None, corner_gap=None,
return_angle=90, return_direction="same", hem=None, teardrop_radius=None,
slots=())`
bends a flange on
one edge of the outline and answers a new part; the part given is left
alone. The flange is a bend of the spec's inside radius, or its own, then a
straight leg `length` long.

- `angle` is the bend's angle in degrees, above 0 and at most 180. A flange
  at 180 degrees is an open hem: its leg comes back over the base (or under
  it, bent down), parallel to it and clear of it. A hem is refused when its
  bend radius is 0, and on an edge that shares a corner with another
  flange, whichever was made first, since the legs would meet, unless the
  hem is inset at least the thickness at that corner.
  `outside_setback()` and `bend_deduction()` have no value at 180.
- `hem` makes the flange a hem by name; left as None the flange is what
  `angle` says, an open hem at 180. `hem="closed"` folds the leg flat onto
  the base: half a turn with no bend radius, the leg's face on the base's,
  the part two thicknesses thick there. `hem="teardrop"` turns the bend past
  half a turn round an inside radius of `teardrop_radius`, the flange's own
  bend radius when left out, until the free end of the leg comes down to
  the base and stops a tenth of the thickness short of it, so the loop
  stays open at the bend and all but shut at the edge; `teardrop_angle()`
  gives the angle, which is what the part keeps and the flat's note says,
  such as `UP 190.849 R2`. `length` is the hem's leg. A hem unfolds as every
  bend does, by the sheet's own K-factor over the angle it turns, with no
  formula to enter: a closed hem by half a turn at radius 0, a teardrop by
  its angle at its radius. With `hem`, leave `angle` out, or give 180; a
  closed hem takes no `bend_radius`, a teardrop's is its `teardrop_radius`,
  which is above a tenth of the thickness, and neither takes a return or a
  length to the outside. Beside another flange a hem by name is inset as an
  open hem is. A tray's rim rolled outward:
  `flange(tray, (1, "free"), 6, direction="down", hem="teardrop", teardrop_radius=1.5)`;
  a safe edge folded flat: `flange(part, 1, 10, hem="closed")`.
  `hem_of()` reads a flange's record as `"open"`, `"closed"`, `"teardrop"`
  or None.
- `direction` is `"up"`, along the plane's normal with the bend's inside on
  the top face, or `"down"`, against it with the inside on the bottom face.
- `start_inset` and `end_inset` leave that much of the edge unbent at its
  start corner and its end corner, so the flange is shorter than its edge.
- `relief=True` cuts a bend relief beside each inset end: a slot the
  sheet's thickness wide and `relief_depth()` deep, the bend radius plus the
  thickness, into the base from the edge, so the bend can form without
  tearing the sheet beside it. Each inset used must then be at least the
  thickness.
- `bend_radius` bends this flange alone with that inside radius, 0 or more;
  left as None it is the spec's. The flat pattern works the flange's bend
  allowance and relief depth from it, and its note names it, such as
  `UP 90 R4`.
- `holes` are round holes cut through the flange's leg, each a
  (u, v, diameter): u along the edge from its start corner, v along the leg
  from where the bend ends. Each lies wholly inside the leg, between the
  insets and short of the bend and the leg's end, and clear of the others.
  On the flat they follow the base's holes, at u along the edge and the
  bend allowance plus v out from it.
- `cutouts` are rectangles cut through the flange's leg, each a
  (u, v, width, height) centred at (u, v) as a hole is placed, its width
  along the edge and its height along the leg. Each lies wholly inside the
  leg by the holes' rule and clear of its holes and the other cutouts. On
  the flat each lies on the strip as its four corners.
- `slots` are rounded slots cut through the flange's leg, each a
  (u1, v1, u2, v2, width): the centres of its two round ends, u and v as a
  hole's, and its width, in any direction. Each lies wholly inside the leg,
  clear of its holes, its cutouts and the other slots; one that reaches the
  bend zone (v within half its width of 0) is refused saying so, naming the
  slot. On the flat its centres follow the leg's holes. A slot that would
  cross a bend, or holes and slots across several faces, are not made here.
- `return_length` above 0 makes a return flange: a second 90 degree bend of
  the flange's radius at the leg's free end, turning the same way as the
  first, then a straight return leg that long, so an up flange's return
  points back over the base, as a channel's lip. Only a 90 degree flange
  takes one. On the flat the strip runs on by a second bend allowance and
  the return length, with a second bend after the first.
- `return_angle` and `return_direction` bend the return its own way.
  `return_angle` is the return's bend in degrees, above 0 and below 180, 90
  when not given. `return_direction="same"` turns it in, the way the flange
  itself is bent, back over the base; `"opposite"` turns it out, so the
  return runs on away from the base as the top of a Z does. The return
  unfolds as every bend does, by the sheet's K-factor at its own angle, and
  its bend on the flat reads up or down as it turns: an up flange's return
  turned out is a down bend. With `length_from="outside"` the leg and the
  return lose the setback at `return_angle`. Either is refused with no
  `return_length`. No corner treatment shapes a return that is not 90
  degrees `"same"`: where it would overlap another flange it is refused,
  inset it clear instead, and its free edge takes no flange. A lip at 120
  degrees turned in: `flange(part, 1, 20, return_length=10, return_angle=120)`;
  a lip turned out: `flange(part, 1, 20, return_length=10, return_direction="opposite")`.
- `length_from="outside"` takes `length` to the outside mould line, where
  the base's outside face and the leg's outside face meet, as a drawing
  dimensions a flange: the straight leg is `length` less `outside_setback()`
  at the flange's own bend radius, so 24 mm to the outside of a 90 degree
  flange on a 2 mm sheet with a 2 mm radius is a 20 mm leg. With a return,
  `length` runs outside to outside, so the leg is less both bends'
  setbacks, and `return_length` runs to the return's outside mould line, so
  the return leg is less its bend's setback: 40 with a 15 mm return on that
  sheet is a 32 mm leg and an 11 mm return. It is refused on a hem, which
  has no setback, and when it leaves no leg or no return leg, naming the
  least length allowed. The part keeps
  the leg, so its flat pattern is the leg's. The `sheet_flange` tool takes
  it, and a model.py line says `length_from="outside"` only when it is set.

## Corners

Where the return legs of two flanges meet at a corner, in one plane, a
corner treatment shapes them in the part and in the flat alike:

- `"mitre"`: both cut back to the line from the corner to where their inner
  edges cross, half the corner each when the returns are alike;
- `"square"`: the earlier return runs through and the later stops short;
- `"open"`: both stop short of the other;
- `"none"`: nothing, which is refused when they would overlap.

Each leaves `corner_gap` between the two, the sheet's thickness when not
given. `corner_treatment` on `flange` is one treatment for both its corners
or a dict of them by the outline's corner number; the part's own, from
`base_flange`, is used where a flange gives none, and mitre where neither
does, said in the part's notes. A flange whose leg, bends or return would
overlap the part anywhere is never built: it is refused with the overlap's
size and place, "would overlap the part by 21 x 21 x 2 mm at (...)", and
what to do instead. The flat's outline, its DXF and its cut length follow
the treatment.

## A flange on a flange's edge

`edge` is a number for an edge of the base's outline, or `(n, where)` for an
edge of the flange already on edge n:

- `(n, "start")` and `(n, "end")` are the two ends of that flange's leg, at
  the start corner and the end corner of edge n. Each runs from the leg's
  bend to its free end, or to its return's bend, so it is as long as the
  leg, and `start_inset`, `end_inset` and a hole's u are measured along it
  from the bend.
- `(n, "free")` is the free edge of its return, or of its leg when it has no
  return. It runs as edge n does, between that flange's insets.

The length, the angle, the insets, the bend radius, `return_length`,
`length_from`, the holes, the cutouts and the corner treatment mean what
they mean on an edge of the base; only `relief` is refused. `"up"` turns
towards the inside face of what the flange stands on, the side that piece's
own bend has its inside, and `"down"` away from it: on a return's free edge
`"up"` goes on round as the return did and `"down"` turns back outward. An
edge takes one flange, and a flange that would overlap the part is refused,
as on the base. The part's record names the flange by its `(n, where)`,
through cuts on its leg and its return are kept as on any other, and the
flat pattern, the bend table, the DXF, the SVG, the mass and a drawing's
flat view all take it in: on the flat it unfolds beyond the edge it stands
on. A flat that would lie over itself is refused by `flat_pattern()`, and
`refold_distance(part)` folds the flat's outline back up and answers how far
it stands off the part, 0 for a flat that is the part's.

Where a flange on a flange's edge meets another flange in one plane, at
right angles, the corner treatment shapes the two, whichever of them is a
leg or a return:

- `"mitre"` cuts each back to its side of the diagonal of their corner
  square, half the gap from it, as a picture frame's corner. A return, or a
  leg with a free edge, that stops up to two bends short of the other is
  carried on to the diagonal, and a bend the other would lie over is cut
  back to clear it by the gap. Two legs that both stand on walls, as two end
  plates do, are mitred from the walls' outer corner to where their returns'
  outside faces cross, and each one's return stops the gap short of the
  other's;
- `"square"` stops the later flange the gap short of the earlier, which runs
  through; `"open"` stops both; `"none"` does nothing.

A dict of treatments names such a corner by the other flange's
`(n, where)`, or by the outline's corner number that the end of a leg stands
at. A flange is not put on a free edge that a corner treatment has cut back
unless it is inset to clear the cut.

## The allowances

The flat is laid out with three pieces of arithmetic, each for a bend
angle in degrees and a spec:

- `bend_allowance()`, the length of the neutral fibre through the bend:
  the angle in radians times (bend radius + K-factor x thickness).
- `outside_setback()`, how far the outside mould line lies from where the
  outside face turns: tan(angle / 2) x (bend radius + thickness).
- `bend_deduction()`, what comes off the two outside flange lengths to give
  the flat length: twice the outside setback less the bend allowance.

## Checked against

The flat lengths are held to the hand formulas, worked in the test itself
and not by the functions above, for every combination of bend angles 15, 30,
45, 60, 90, 120, 135, 150 and 170 degrees; thicknesses 0.5, 1, 1.5, 2, 3
and 6; inside radii of 0, half, one and two thicknesses; K-factors 0.3,
0.33, 0.44 and 0.5; and lengths given as the leg and to the outside: one
bend, two bends, a return and an open hem, each to 1e-6 mm.

- BA = angle (radians) x (R + K x T)
- OSSB = tan(angle / 2) x (R + T)
- BD = 2 x OSSB - BA

With a leg given, the flat is the base plus BA plus the leg for each bend.
With lengths to the outside, it is the two outside lengths less BD. A few of
the rows, each on a base 50 long flanged on its far edge:

| Case | Angle | T | R | K | Lengths | BA | OSSB | Flat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| one bend | 90 | 2 | 2 | 0.44 | leg 40 | 4.524 | 4.000 | 94.524 |
| one bend | 45 | 1.5 | 1.5 | 0.33 | outside 250 | 1.567 | 1.243 | 300.324 |
| two bends | 120 | 3 | 6 | 0.5 | leg 40 each | 15.708 | 15.588 | 161.416 |
| return | 90 | 2 | 2 | 0.44 | outside 60, return 25 | 4.524 | 4.000 | 132.048 |
| open hem | 180 | 1 | 0.5 | 0.3 | leg 20 | 2.513 | - | 72.513 |

## The flat pattern

`flat_pattern()` unfolds a sheet part from its record. Each flanged edge of
the outline is pushed out by its bend allowance plus its flange's length,
over the span between its insets, and each flange gives one bend with its
two bend lines, where the bend starts on the base's edge and where it ends a
bend allowance further out, its angle, its direction and its inside radius.
Relief slots are cut into the outline, the base's holes lie on the flat
where they lie on the base, and each flange's holes and cutouts lie on its
strip, a flange's cutout as its four corners, since a strip may run at any
angle. A hem unfolds by half a turn's bend allowance. The slots, the base's
where they lie on it and a leg's by their centres as its holes, are the
flat's `slots`, each (x1, y1, x2, y2, width).

`write_flat_dxf()` writes it as an AutoCAD 2000 DXF in millimetres: the
outline and each cutout, the base's and then the flanges', as a closed
polyline and each hole as a circle on layer CUT, each slot as two LINE
and two ARC entities on CUT, its sides and its round ends, each
bend as one line down the middle of its zone on layer BEND, which is drawn
DASHED (12.7 mm on, 6.35 off, defined in the file itself), and a note
beside each bend on layer NOTES, such as `UP 90 R2`. With `bend_zones`,
the two edges of each bend zone follow on layer BEND-ZONE, continuous.
`write_flat_svg()` writes the same as an SVG, +y up, with the bend's centre
line dashed. `flat_solid()` gives the flat as a solid, the outline
extruded by the thickness from z = 0 with every hole and cutout, the
flanges' among them, cut through it, and
`write_flat()` picks by the file's suffix: .svg is SVG, .step or .stp that
solid as STEP, and anything else DXF. Given a `title`, the DXF and SVG
writers put it once below the flat, followed by the thickness, such as
`tray, 2 mm`: `NOTE_HEIGHT` high, its baseline `NOTE_HEIGHT` under the
outline's lowest point, a TEXT on NOTES in the DXF and a text in the SVG;
the STEP solid ignores it, and with no title every byte is as before.
`dxcad flat --title` writes the part's name as the title. The same part always gives the same
DXF and SVG bytes.

`bend_table()` answers one row per bend of the flat, in its order, for the
press brake: its number from 1, its angle, its direction, its inside
radius, its bend allowance worked with that radius, and the length of its
bend lines.

`edge_table()` answers one row per edge of a sheet part's outline, in
order, for choosing where a flange goes: its number from 0, as `flange()`
takes it, its start and end (x, y), its length, and the flange on it as
its note (such as `UP 90 R2`) and leg length, or None for both when the
edge is free. `edge_row_text()` says a row as `dxcad flat --edges` prints
it.

`flat_cut_length()` answers how far the cut runs, in mm: the outline's
perimeter plus every hole's circumference and every cutout's perimeter,
the base's and the flanges', and every slot's, 2 (L - W) + pi W for one L
long end to end and W wide. `flat_area()` answers the flat's area in mm²,
the outline's less every hole, cutout and slot. Together they quote a laser
or a plasma table. `dxcad flat` counts the slots on its size line, after
the holes and cutouts.

A drawing of a sheet part, or of its flat, shows each slot, and a view that
sees slots face on names them under it in its holes note, in their own
groups after the holes: `SLOT 90 x 10`, length end to end then width, with
`2x` before it for two alike. `dxcad describe` and the `sheet_*` tools list
a sheet part's slots as they do its holes.

`flat_annotations(pattern, edge="left")` answers what is written on a flat
besides its cut and bend lines, each where it goes:

- `bend_labels()`: a label for each bend, its number in the bend table and
  its note, such as `3: DOWN 90 R1.5`, turned along its bend line and set
  beside it, then moved along the line, to its other side or further off
  until it touches no other label, crosses neither the outline nor
  another bend's line, and lies on the sheet. A label with no such place,
  on a bend shorter than its words, is written level to the right of the
  blank. `labels_meet()` and `label_crosses()` say whether two labels
  touch and whether one touches an outline.
- `blank_size()` and `blank_rectangle()`: the rectangle the flat is cut
  from, written as `BLANK 294.57 x 249.57 mm` over its upper left corner.
- `bend_distances(pattern, edge)`: how far each bend's centre line lies
  from an edge of the blank, `"left"`, `"bottom"`, `"right"` or `"top"`. A
  line along the chosen edge is measured from it and a line across it
  from the edge that makes the corner with it, so a flat's distances are
  all from one corner of its blank; a line at any other angle has none.
- `flat_table(pattern, edge)`: the bend table as the flat carries it,
  headed BEND, ANGLE, DIR, RADIUS, ALLOWANCE, FROM, DISTANCE and ORDER. The
  allowance is the sheet's own, from its K-factor. ORDER is empty: the
  order the bends are made in is the bender's to fill in.

`flat_dxf_text()`, `flat_svg_text()` and `write_flat()` take
`annotated=True` and `datum=` to write them: the labels on NOTES in place
of the note at each bend's middle, the blank on BLANK and the table on
BEND-TABLE, CUT and BEND as they were. Without it a flat is written as it
always was. The window's Show Flat Pattern draws them and its Export Flat
Pattern writes them.

From the command line, `dxcad flat` writes a part's flat pattern from a
project's model.py, and `dxcad flat --all` every sheet part the model
registers; with `--edges` it prints the edge table after the size line,
a line per edge such as
`edge 1: (100, 0) to (100, 50), 50.000 mm, flange UP 90 R2 20.000 mm`; with
`--bends` it prints the bend table too, a line per bend
such as `bend 1: UP 90 R2, allowance 4.524 mm, length 50.000 mm`, and
with `--cut` the cut length and area, such as
`cut length 349.048 mm, area 6226.195 mm²`, and then the flat's mass in
its sheet's metal, such as `mass 97.751 g, mild steel`; see
[cli.md](cli.md#flat).

## A worked tray

A 100 x 50 mm base of 2 mm sheet with a 10 mm hole, a 20 mm flange up on
the right-hand edge, inset 10 and 15 mm with relief, and a 15 mm flange bent
down 45 degrees on the left-hand edge:

```python
spec = SheetSpec(2, 2, 0.44)
tray = base_flange([(0, 0), (100, 0), (100, 50), (0, 50)], spec, holes=[(50, 25, 10)])
tray = flange(tray, 1, 20, start_inset=10, end_inset=15, relief=True)
tray = flange(tray, 3, 15, angle=45, direction="down")
part("tray", tray)
```

It is one solid of volume 12782.159 mm³: the base's 10000 less the hole's
50π, the right flange's bend and leg, 75π + 1000, less its two 16 mm³
relief slots, and the left flange's bend and leg, 75π + 1500. Its flat
pattern is 141.786 x 50.000 mm with 2 bends and 1 hole: saved as a model.py,
run into a project with `dxcad run` and unfolded with `dxcad flat` and
`--part tray`, that is the size line it prints.

## A hemmed clip

The same base with an open hem 15 mm long on the right-hand edge, bent with
its own 3 mm radius, and a 30 mm flange up on the left-hand edge with an
8 mm hole through its leg, 25 mm along the edge and 15 mm out from the bend:

```python
spec = SheetSpec(2, 2, 0.44)
clip = base_flange([(0, 0), (100, 0), (100, 50), (0, 50)], spec)
clip = flange(clip, 1, 15, angle=180, bend_radius=3)
clip = flange(clip, 3, 30, holes=[(25, 15, 8)])
part("clip", clip)
```

It is one solid of volume 16127.345 mm³: the base's 10000, the hem's half
turn of 3 to 5 mm radius and its leg, 400π + 1500, and the left flange's
bend and leg, 150π + 3000, less its hole's 32π. Its flat pattern is
161.713 x 50.000 mm with 2 bends and 1 hole, the hem's note `UP 180 R3`;
`dxcad flat` with `--part clip` prints that size line, and with
`--output clip.step` writes the flat as a solid.

## A worked channel

A 200 x 60 mm base of 2 mm sheet with a 2 mm bend radius and DIN 6935's
K-factor, and a 90 degree flange up on each long edge, each 25 mm to the
outside mould line, as a drawing dimensions it, with a return 10 mm to its
outside mould line:

```python
spec = SheetSpec(2, 2, din_k_factor(2, 2))
channel = base_flange([(0, 0), (200, 0), (200, 60), (0, 60)], spec)
channel = flange(channel, 0, 25, return_length=10, length_from="outside")
channel = flange(channel, 2, 25, return_length=10, length_from="outside")
part("channel", channel)
```

The K-factor is 0.325. Each 25 mm runs outside to outside, from the
base's outside face to the return's, so the leg is a 17 mm leg, 25 less
the outside setback of 4 at each of its two bends, and each 10 mm return
is a 6 mm return leg, 10 less its bend's setback. It is one solid of
volume 49939.822 mm³: the base's 24000, and on each side two bends, 600π
each, a leg of 6800 and a return of 2400. Saved as a model.py, run into a project
with `dxcad run` and unfolded with `dxcad flat --part channel --bends
--cut`, it prints, after the path written:

```text
200.000 x 122.650 mm, 4 bends
bend 1: UP 90 R2, allowance 4.163 mm, length 200.000 mm
bend 2: UP 90 R2, allowance 4.163 mm, length 200.000 mm
bend 3: UP 90 R2, allowance 4.163 mm, length 200.000 mm
bend 4: UP 90 R2, allowance 4.163 mm, length 200.000 mm
cut length 645.301 mm, area 24530.088 mm²
mass 385.122 g, mild steel
```

## A worked corner post

A door's corner post, 130 x 120 x 200 over its walls, bent from one 1.5 mm
sheet with a 1.5 mm radius: [corner_post.py](examples/corner_post.py).
Looking down on it, wall B runs along the bottom and is the base flange, on
`Plane.XZ`; wall A stands up the left with flange C turned in off it and lip
D turned outward off flange C; flange E stands up the right with lip F
turned in. Every length is to the outside:

```python
spec = SheetSpec(1.5, 1.5, 0.44)
post = base_flange([(3, 3), (127, 3), (127, 197), (3, 197)], spec, Plane.XZ)
post = flange(post, 3, 120, 90, "down", return_length=23.5, length_from="outside")
post = flange(post, 1, 20, 90, "down", return_length=10, length_from="outside")
for edge in (0, 2):
    post = flange(post, edge, 20, 90, "down", return_length=10,
                  length_from="outside", corner_treatment="square")
post = flange(post, (3, "free"), 10, 90, "down", length_from="outside")
for end in ("start", "end"):
    post = flange(post, (3, end), 26.5, 90, "up", return_length=10,
                  length_from="outside", corner_treatment="mitre")
part("corner_post", post)
```

The first four are flanges on the base's edges: wall A with flange C, flange
E with lip F, and wall B's two end flanges, square at lip F, which runs its
whole height while each end lip stops 1.5 short of its free edge. The last
three stand on wall A's flange. `(3, "free")` is lip D, on the free edge of
flange C and turned away from the post's inside. Its bend stands a bend
radius beyond that edge, so flange C is given as 23.5 and lip D's outside
face is 26.5 from wall A's. `(3, "start")` and `(3, "end")` are wall A's own
ends, at the top and the bottom of the post, each turned over the post with
a 26.5 mm end flange and a 10 mm lip, which puts that lip in lip D's plane.
There the end lip is carried on past flange C and the two meet on a
45 degree joint, each 7 mm of straight leg, with lip D's bend cut back
under it; and the end flange is mitred against wall B's from the walls'
outer corner. It is one solid of volume 108213.389 mm³, and `dxcad flat
--part corner_post` unfolds it as one piece, 303.465 x 262.572 mm, with 13
bends.

## In the window

The Sheet Metal toolbar and menu hold four actions, Base Flange, Flange,
Export Flat Pattern and Show Flat Pattern; see [gui.md](gui.md). Base
Flange makes the closed sketch in hand a sheet part, a line-tool outline or
one rectangle with the circles drawn inside it as holes, the rectangles
drawn inside it as cutouts and the slots drawn inside it with the slot tool
as slots, and asks the metal and then its gauge from the
table, or Custom for the thickness, the bend radius and the K-factor as
numbers. Flange bends one on an edge of the picked sheet part, or on an
edge of a flange it already has, the two ends of its leg and its free edge,
which its Edge list names after the outline's and a click in the view
chooses ([the corner post, in the window](tutorials/corner-post.md)), asking the
edge, the length, the angle (180 for an open hem), the direction, a
closed or a teardrop hem by name with the teardrop's radius, the two
insets, whether to cut relief, the flange's own bend radius, offered as the
sheet's, its return length, offered as 0, the holes through its leg, as one
line `u, v, d; u, v, d`, the cutouts through its leg, as one line
`u, v, w, h; u, v, w, h`, and the slots through its leg, as one line
`u1, v1, u2, v2, w; ...`, each empty for none, each checked as it is typed
and shown on the faint preview. With All edges ticked it
bends one on every free edge of the outline, each from its row of a table,
and a flange already made is changed by a double click on its row in the
Feature tree ([the Flange dialog](gui.md#the-flange-dialog)). Export
Flat Pattern writes the picked part's flat as a DXF, or as an SVG when the
name chosen ends .svg. Show Flat Pattern draws the picked part as its flat
solid in its place, and again draws it formed: a view, not a part, so it
writes nothing and the part is counted once. Base Flange and Flange write
their line into the model, so the model stays the part, and one Undo
takes each back. Bend Table, at the end of the Sheet Metal
menu and not on its toolbar, shows the picked part's bend table in a box,
a line per bend as `dxcad flat --bends` prints it, or `No bends.`; it
changes nothing.

## Over the agent door

`dxcad serve` offers the same as five tools; see
[agents.md](agents.md). `sheet_base_flange` makes a part from an outline,
a thickness, a bend radius, a K-factor (DIN 6935's, as `din_k_factor()`
gives it, when the agent leaves it out), any holes and any `cutouts`, each
[x, y, width, height]; `sheet_flange` bends
a flange on one of its edges, with the angle (180 for a hem), the
direction, the insets, relief, its own `bend_radius`, a `return_length`
and any `holes`
through its leg, each [u, v, diameter] with u along
the edge from its start corner and v along the leg from where the bend
ends, and any `cutouts` through it, each [u, v, width, height]; `flat_pattern` writes its flat as a DXF, or an SVG for a name ending
in .svg, or the flat solid as STEP for one ending in .step or .stp, and
answers its width, its height, its bend count and its `bend_table`, a row
per bend as `bend_table()` gives it, then its `cut_length` and `area` as
`flat_cut_length()` and `flat_area()` give them; `sheet_flat_part`
adds the flat solid to the document as a part of its own, named by its
`result`; and `sheet_edges` reads a part's edge table, as `edge_table()` gives it, with
its thickness, bend radius and K-factor, and changes nothing.

## Limits

- A flange goes on an edge of the base's outline, or on an edge of a flange
  that stands on one: the two ends of its leg and its free edge. A flange on
  a flange's edge takes no further flange, and one edge takes one flange.
- Flanges on the two edges of a convex corner leave that corner open on
  the flat. Flanges on the two edges of a reflex corner, or of a straight
  one where two edges run on in one line, cannot be unfolded, and
  `flat_pattern()` says so.
- Holes are round, through the base or through a flange's leg; none may
  reach into a bend. Cutouts are rectangles, through the base square to the
  plane's axes or through a flange's leg square to its edge; the return
  leg takes none.
- Still refused: a bend above 180 degrees that is not a teardrop hem's, a
  flange at 180 with a bend radius of 0 that is not named `hem="closed"`,
  and a hem on an edge that shares a corner with another flange when the
  hem is inset less than the thickness at that corner.
- A teardrop hem's free edge stops a tenth of the thickness short of the
  base and does not touch it; a closed hem's leg and the base are one solid
  where they lie face to face, so a hole through the base there is covered
  by the leg, and a cut through the two at once is not kept as sheet metal.
- A length to the outside mould line is refused on a hem, which has no
  setback, and when it leaves no straight leg; the part keeps the leg, so
  the edge table and the bend table show the leg, not the length given.
- The edge table, the bend table and the cut length and area are worked
  from the part's record, as the flat is; a flat's title goes on its DXF
  and SVG, not on its STEP solid.
