# Where the fastener figures come from

Most of the numbers in these models are shape: how long a plate is, how thick
a wall is, how far apart two holes sit. Those are chosen, and changing one is
the whole point of a parametric model.

A few are not chosen. A hole that an M4 screw has to pass through, a drill
that an M4 thread is cut into, a seat that an M4 socket head has to sit in:
each of those has one right answer and it comes out of a table. This page is
that table for every such figure in the examples, so that nobody has to guess
whether a number was looked up or made up.

Every row was checked against its standard by hand on 2026-09-21.

## The table

| Model | Constant | Value | What it is | Standard |
| --- | --- | --- | --- | --- |
| flange.py | `BOLT` | 9.0 | Clearance hole for M8, medium series | ISO 273 |
| knob.py | `NUT` | 10.0 | Width across the flats of an M6 hexagon nut, which the pocket holds captive | ISO 4032 |
| knob.py | `NUT_DEPTH` | 5.0 | How deep that pocket is; an M6 nut is about 5.2 thick, so it stands a little proud | ISO 4032 |

## The three holes one thread asks for

One thread size asks for three different holes, and the table's rows are
each one of them.

- **The clearance hole.** The screw passes through and does not bite, so
  the hole is larger than the thread. ISO 273 gives three series: fine 8.4,
  medium 9.0 and coarse 10.0 for M8. `flange.py` takes the medium one, which
  is what a part with ordinary tolerances wants.
- **The tapping drill.** The thread is cut into this hole, so it is smaller
  than the thread: the nominal diameter less the pitch, which for M4 coarse
  is 4.0 - 0.7, a 3.3 drill (ISO 2306).
- **The counterbore.** A socket head screw's seat has to clear its head
  across and in height, to sink the head below the face: for an M4 ISO 4762
  screw, whose head is 7.0 across and 4.0 high, DIN 974-1 gives 8.0 across,
  and 4.4 deep leaves 0.4 over it.

## Figures that are a fastener's nominal size and not a table value

These name a thread and take its nominal diameter, which is not what any of
the tables above would give. They are here so that nobody reads them as
looked-up numbers.

| Model | Constant | Value | What it is |
| --- | --- | --- | --- |
| bracket.py | `HOLE_DIAMETER` | 5.0 | The worked example's own figure, about an M5's nominal |
| clip.py | `SCREW` | 4.0 | An M4's nominal diameter, tighter than any ISO 273 series |
| knob.py | `BORE` | 6.0 | An M6's nominal diameter, the screw the captive nut takes |

Every other number in the examples is shape and comes from nowhere but the
part itself.
