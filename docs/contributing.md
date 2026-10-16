# Contributing

The rules for a contribution are kept in one place,
[CONTRIBUTING.md](https://github.com/faizaldm/DX-CAD/blob/main/CONTRIBUTING.md)
at the root of the repository: how to set up, the four commands a change
must pass, the form a piece of work is proposed in, and the sign-off every
commit carries. This page walks one first contribution through them: a new
part for the [gallery](gallery.md), from an empty file to a signed-off
commit. Every command below is run from the root of a checkout, with the
environment [SETUP.md](https://github.com/faizaldm/DX-CAD/blob/main/SETUP.md)
makes.

## 1. Start a part

`dxcad gallery new` writes a starter model.py into docs/examples and adds
its row to the examples' index, in name order. The name is a Python
identifier no example has yet:

```
dxcad gallery new bracket_two
```

The starter is three numbers and a box made of them, with a docstring to
fill in: its first line is the part's title in the gallery, the paragraph
after it the line shown below the title, and its `Tags:` line the group it
is shown in, from solid, sketch, sheet, mates, assembly, drawing and text.
Make the part yours: change the numbers and the model, and write the
docstring. A model imports nothing; every name it needs is in scope, as
[the model language](kernel.md) lists them.

## 2. Check it as the suite checks ours

`dxcad gallery check` runs the part the way the test suite runs the shipped
examples, one line each: the SPDX first line, the docstring's title and
tags, no import, that it builds at least one part within 60 seconds, that
every part is valid, and that it builds again with its first number
changed. It exits 0 only when every line says `ok`:

```
dxcad gallery check docs/examples/bracket_two.py
```

The starter passes as it is written, so a line that fails is something the
edit changed.

## 3. Write the item

Work is queued in
[BACKLOG.md](https://github.com/faizaldm/DX-CAD/blob/main/BACKLOG.md), one
item per change. A part for the gallery is one item, for example:

```text
- [ ] 620. A second bracket for the gallery (S)
  A bracket with a gusset, to show a part the sketch tools make.
  Accept: dxcad gallery check passes on docs/examples/bracket_two.py and
  its picture is in docs/gallery.
```

Ideas come as an ordinary issue, in your own words, and the owner writes the
backlog from them; once your item is queued, check the file's format:

```
python -m dxcad.backlog check BACKLOG.md
```

## 4. The four commands

A change is ready when all four pass. The picture comes last:
`python -m dxcad.gallery` draws every example into docs/gallery, and
`python -m dxcad.docsgen gallery` writes the gallery page again.

```
python -m compileall -q src tests
python -m pytest
python -m ruff check src tests
python -m dxcad.smoke
```

## The performance baseline

`python -m dxcad.bench` times, for every example, building its model, 30
offscreen frames of it orbiting and making its drawing, and writes
bench.json. CI's bench job runs it on Linux, keeps bench.json as an artifact
of the run, and holds it to `bench-baseline.json` at the root of the
repository: a measure more than twice its baseline fails the job, naming the
example and the measure. A baseline taken on another platform is not
compared, and the job says so.

A change that is slower on purpose, or a new example, refreshes the
baseline in the same pull request. Download bench.json from the bench job of
a run on main, save it over `bench-baseline.json`, and say why in the commit.
On your own machine the same is

```
python -m dxcad.bench --output bench-baseline.json
```

but a baseline only holds runs on the platform it was taken on, so the one
to commit is CI's. The first baseline was taken on Windows, so CI's Linux
runs are not compared until it is refreshed from one of them.

A large assembly has a baseline of its own, `bench-assembly-baseline.json`:
opening and rebuilding a generated 200-part assembly, each the quickest of
five. A slow test, run in the serial pass, fails when either is more than 25
percent slower than it on the platform it was taken on.
`python -m dxcad.bench --assembly --output bench-assembly-baseline.json`
takes it again, on a quiet machine, after a change that is slower on purpose.

A drawing's annotations have limits and no baseline. `python -m dxcad.bench
--drawing` opens the drawing of the engine example, 192 parts in four views,
in a window of its own, and times an annotation added, dragged and deleted,
each under 0.1 s with its repaint, and fifty put on as one change, under 1 s.
A slow test in the serial pass runs it and fails on any of them.

A drawing's first changes are held to its fourth. `python -m dxcad.bench
--first-changes` opens the drawings of the engine and gearbox examples on an
A1 sheet with no parts list and makes four changes to each with a tool of
three clicks, by the sheet's own mouse, the tool's hover shown between the
clicks: the first, the second and the fourth are each under 1 s in total, and
what opening the drawing spends on making ready for them is under 2 s. A slow
test in the serial pass runs it on each example and fails on any of them. The
tool is the benchmark's own and does nothing of its own: what an add-on's
tool works out at its first hover is the add-on's time, not measured here.
Each drawing is then opened afresh and measured with a second tool, made as
an add-on's linear dimension is (item 864): its hover snaps to the edges the
view draws, read with their parts from `document.view_lines(view,
parts=True)`, its run reads the drawing's annotations, its dimension is a
real one on the dimension layer, and its plugin's `drawing_ready` call is
made as the drawing opens; its rows read "engine_inline4 dimension" and
"gearbox dimension", held to the same limits. Each drawing is then measured
a third time (item 867), the dimension made as Drafting Pro's sweep makes it,
by a hand on the window: the drawing opened in the window's own tab, the
window 1500 by 1000, the tool chosen by its menu entry, QTest's pointer moved
to each point and the window let handle its events, the hover waited for,
and QTest's click on the ends of a line the front view draws; its rows read
"engine_inline4 by hand" and "gearbox by hand", held to the same limits. An
add-on whose own first change is slow works out what its tools need in
`registry.drawing_ready`: a hover that projects the parts near the pointer
itself, as a hidden-line run per part, spends seconds the first time on
each part and view, on the hover's thread but holding the interpreter, so
the window waits with it.

`python -m dxcad.sweep_drawings` goes through every drawing command of the
window on the engine and gearbox examples as a user does, a view moved, the
scale, the parts list's columns, Delete, Undo, Redo, Add View and Add Part
Sheets, and writes build/sweep/drawings.md: a row a command with its time,
whether the result is where the clicks put it and inside the sheet, what
Undo calls it, what F1 showed of its steps, whether "Please wait" showed,
and a picture. It fails on a command over a second or out of place. What is
still over a second is named in tests/sweeps/drawings-known.txt, which
`--known` passes over and which can only shrink. After the models it draws
every sketch tool's figure by its own clicks, a line, a polyline open and
closed, a rectangle, a circle, both arcs, a polygon, a slot, an ellipse and a
spline ended each way, closed by Close Sketch and opened by Break, in a sketch started from the
Sketch menu and in one started by `window.start_sketch`, and fails on a
figure that is not in the model's own line or that a run of the model does
not make again.

The compiled build reads no annotation as a type: setup.py compiles inside
`dxcad.compiled.annotations_as_hints()`, since Cython 3.3.0 otherwise holds
what a loop over `names: list[str]` gives to `str` exactly, whatever
`annotation_typing` says, and a compiled DX-CAD then refuses values its
source takes. The build stops if its compiler still writes such a check.

Python the suite runs is not always Python Cython takes: `min([low, *reached])`
passed every test and stopped the compiled build with "starred expression is
not allowed here". `tests/test_cython_takes.py` runs Cython's translation step
alone, to C with the build's directives and no C compiler
(`dxcad.compiled.translation_errors`), on every compiled module that differs
from `main`, in seconds, and on the whole core in a test marked slow. A
failure names the file, the line and Cython's words; write the line another
way, as `min([low] + reached)`.

## 5. Commit, signed off

Every commit carries a Developer Certificate of Origin sign-off, which
`git commit -s` adds from your git name and e-mail; CONTRIBUTING.md says
what it certifies. Then open a pull request that names the item's number.
