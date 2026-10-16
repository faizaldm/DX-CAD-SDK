# DX-CAD for agents

`dxcad serve` is a Model Context Protocol server. An MCP client, Claude Code
or Claude Desktop, starts it as a child process and talks to it down its
standard input and output; the server holds one document of named solid
parts, in millimetres, and every tool below makes, changes, measures, reads
or writes those parts. Nothing is drawn: a tool that makes or changes a part
answers its facts, its volume, its size, its faces by kind and its round
holes, and that answer is the agent's only look at the part. There is no
window and no Qt in the server, so it runs on a machine with no display.

The worked example, a bracket with four holes from one sentence, is in
[examples/bracket.md](examples/bracket.md). It runs its model with `run_model`
and `model_set`, so the server needs `--allow-run` for it: see
[What it runs](#what-it-runs).

## Before anything else

Install DX-CAD and check that it works, as README's Install section says:

```
pip install dxcad
dxcad doctor
```

## Claude Code

One line, typed in the directory the parts are to be written in:

```
claude mcp add dxcad -- dxcad serve
```

Or the same thing as a file, `.mcp.json` at the root of a project, which can
be committed so that everyone who opens the project has the server:

```json
{
  "mcpServers": {
    "dxcad": {
      "command": "dxcad",
      "args": ["serve"]
    }
  }
}
```

Both of these find `dxcad` on the PATH, which a terminal with the virtual
environment active has. When it has not, use what the next section uses.

## Claude Desktop

Claude Desktop reads `claude_desktop_config.json`, which Settings, Developer,
Edit Config opens. It is kept at

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

A desktop application is started by the desktop and not by a terminal, so it
has no virtual environment on its PATH and `"command": "dxcad"` is not found
from there; and it starts its servers in a directory of its own choosing,
which is not where the parts should land. DX-CAD writes the configuration
that answers both, naming the Python it is installed under by its whole path
and the directory to work in:

```
dxcad serve --config --directory ~/Documents/parts
```

It prints what goes in the file, which on Windows looks like this:

```json
{
  "mcpServers": {
    "dxcad": {
      "command": "C:\\Users\\you\\.venvs\\cad\\Scripts\\python.exe",
      "args": [
        "-m",
        "dxcad",
        "serve",
        "--directory",
        "C:\\Users\\you\\Documents\\parts"
      ]
    }
  }
}
```

If the file already holds an `"mcpServers"` object, add the `"dxcad"` entry
to it and leave the others. Restart Claude Desktop afterwards; the server is
listed under the tools it offers. The directory has to exist: a
`--directory` that is not there is said on the server's standard error, which
is what the client's log for the server shows.

## What it runs

`run_model` and `model_set` run a model.py, which is Python, with your own
permissions: whatever you may do on the machine, a model may do. That is the
bargain `dxcad run` already makes, and it is what makes a saved project
parametric, but it is the one thing here that is not bounded by the kernel.
The server's annotations say so, `run_model` and `model_set` being the two
tools marked open-world, and a client that asks before a call will ask
before these. `project_save` and `export` write where they are told, and
refuse to write over a file that is already there unless `force` is given.

So the two are off unless you say otherwise. A server started plainly has
neither in `tools/list`, and a call of either is refused in the words a tool
the server has never heard of is refused in, naming the option. `--allow-run`
turns them on:

```
dxcad serve --allow-run
```

It goes into a configuration the same way, after `--directory`, and
`--config` prints it:

```
dxcad serve --config --directory ~/Documents/parts --allow-run
```

Every other tool is there either way: an agent can draw, drill, pattern,
measure, save and export a part without the server running a line of Python.
`--allow-run` is what a parametric model is worth, and what it costs.

## Where it may write

The server works in one directory and reads and writes nowhere else. That
directory is `--directory` when there is one, and where the server was
started when there is not. Every path any tool is given, `project_open`,
`project_save`, `export` and `import_part` alike, is resolved against it
before the file is touched: a relative path is taken from it, an absolute one
has to be inside it, and `..` and symbolic links are followed first, so a
path that leaves the directory by any road is refused in words naming the
path and the directory, with nothing read or written. A model `run_model` is
given has the same directory as its base.

So the directory named in the configuration is the whole of what an agent
can reach through the tools. It is worth giving it one of its own.

## The tools

<!-- generated by python -m dxcad.docsgen agents: the tools -->

| Tool | What it does | Inputs |
| --- | --- | --- |
| `document_list` | List the parts in the document: each one's name, volume and whether it is a valid solid. | none |
| `describe` | Describe one part, or every part when no name is given: volume, area, bounds, size, centre of mass, counts of faces by kind of surface, and each round hole's diameter, depth, axis and centre. This is the only look at a part there is. | `name`: string |
| `printability` | Report how one part would 3D print: its volume, its mass in a named material or at a density, and which it assumed, its centre of mass, how many faces overhang and their area, the thinnest wall and where it is, and a warning for each check it fails. | `name`: string, required; `density`: number; `material`: string; `min_wall`: number; `angle`: number |
| `document_rename` | Give a part another name. | `name`: string, required; `new_name`: string, required |
| `document_remove` | Take a part out of the document. | `name`: string, required |
| `document_duplicate` | Copy a part under a new name. The original stays. | `name`: string, required; `new_name`: string, required |
| `undo` | Take back the last change to the document. Answers whether there was one. | none |
| `redo` | Put back the change the last undo took away. Answers whether there was one. | none |
| `make_box` | Add a box with its edges along the axes. Its lowest corner is at the origin given. | `name`: string, required; `dx`: number, required; `dy`: number, required; `dz`: number, required; `origin`: array of number (3); `color`: string; `part_number`: string; `revision`: string; `properties`: object |
| `make_cylinder` | Add a cylinder standing along Z. The centre of its base is at the origin given. | `name`: string, required; `radius`: number, required; `height`: number, required; `origin`: array of number (3); `color`: string; `part_number`: string; `revision`: string; `properties`: object |
| `make_sphere` | Add a sphere. Its centre is at the origin given. | `name`: string, required; `radius`: number, required; `origin`: array of number (3); `color`: string; `part_number`: string; `revision`: string; `properties`: object |
| `make_cone` | Add a cone or a frustum standing along Z. The centre of its base is at the origin given. | `name`: string, required; `bottom_radius`: number, required; `top_radius`: number, required; `height`: number, required; `origin`: array of number (3); `color`: string; `part_number`: string; `revision`: string; `properties`: object |
| `make_torus` | Add a torus, a ring, lying in the XY plane. Its centre is at the origin given. | `name`: string, required; `major_radius`: number, required; `minor_radius`: number, required; `origin`: array of number (3); `color`: string; `part_number`: string; `revision`: string; `properties`: object |
| `translate` | Move a part by a vector. | `name`: string, required; `vector`: array of number (3), required; `as`: string |
| `rotate` | Turn a part about an axis, by the right-hand rule. | `name`: string, required; `point`: array of number (3), required; `direction`: array of number (3), required; `angle`: number, required; `as`: string |
| `mirror` | Reflect a part in a plane. With "as", this makes the other hand of a part. | `name`: string, required; `point`: array of number (3), required; `normal`: array of number (3), required; `as`: string |
| `scale` | Make a part larger or smaller about a point, which stays where it is. | `name`: string, required; `factor`: number, required; `origin`: array of number (3); `as`: string |
| `cut` | Cut part b out of part a. On a sheet part, give holes and rectangular cutouts with the sheet tools' holes and cutouts, and shape where flanges or returns meet with a corner treatment, rather than cutting: a through cut normal to one face is kept as that face's cutout or hole, a cut across a bend zone or a corner is refused, and any other boolean makes a plain solid that cannot be unfolded. | `a`: string, required; `b`: string, required; `keep`: boolean; `proceed`: boolean; `as`: string |
| `fuse` | Join part b onto part a. | `a`: string, required; `b`: string, required; `keep`: boolean; `proceed`: boolean; `as`: string |
| `common` | Keep only what part a and part b share. | `a`: string, required; `b`: string, required; `keep`: boolean; `proceed`: boolean; `as`: string |
| `hole` | Drill a round hole into a flat face of a part, straight in. | `name`: string, required; `facing`: array of number (3), required; `centre`: array of number (3), required; `radius`: number, required; `depth`: number |
| `countersink` | Drill a hole with a 90 degree cone at its mouth, for a countersunk screw. | `name`: string, required; `facing`: array of number (3), required; `centre`: array of number (3), required; `radius`: number, required; `head_radius`: number, required; `depth`: number |
| `counterbore` | Drill a hole with a wider flat-bottomed bore at its mouth, for a socket head screw. | `name`: string, required; `facing`: array of number (3), required; `centre`: array of number (3), required; `radius`: number, required; `head_radius`: number, required; `head_depth`: number, required; `depth`: number |
| `fillet_all` | Round every edge of a part. Refused, with the part unchanged, if the radius does not fit. | `name`: string, required; `radius`: number, required |
| `chamfer_all` | Cut a flat across every edge of a part. Refused if the distance does not fit. | `name`: string, required; `distance`: number, required |
| `sketch_extrude` | Add a part by drawing a closed outline on a plane and extruding it along the plane's normal. This is how a plate of any outline is made, holes and all. Give constraints to square up a one-loop outline of move_to, line_to and close before it is swept. | `name`: string, required; `plane`: string or object; `profile`: array of object (at least 1), required; `constraints`: array of object; `height`: number, required |
| `sketch_revolve` | Add a part by drawing a closed outline on a plane and turning it about an axis. The outline must lie to one side of the axis. Give constraints to square up a one-loop outline of move_to, line_to and close before it is swept. | `name`: string, required; `plane`: string or object; `profile`: array of object (at least 1), required; `constraints`: array of object; `point`: array of number (3), required; `direction`: array of number (3), required; `angle`: number |
| `text3d` | Add a part that is the letters of a text, swept along a plane's normal. Fuse it with a part to raise the text on it, or place it sunk into a face and cut it to engrave. | `name`: string, required; `text`: string, required; `size`: number, required; `depth`: number, required; `font`: string; `plane`: string or object; `at`: array of number (2); `angle`: number; `align`: one of left, centre, right |
| `mate` | Place a part against another by one mate: coincident (two faces flush), concentric (two axes in line), distance (two faces parallel, value apart) or angle (value degrees). A part's mates are met in order, each keeping what the ones before fixed; answers what freedom is left. | `part`: string, required; `ref`: string, required; `to`: string, required; `to_ref`: string, required; `kind`: one of coincident, concentric, distance, angle, required; `value`: number |
| `suggest_mates` | List the mates a part's features allow against the parts near it, best first: a cylinder to a hole it fits as concentric, opposed faces as coincident (first where a head seats on a hole's face), and as distance with the measured gap. Adds no mate: propose them to the user, and call mate only for the ones the user confirms. | `part`: string, required |
| `measure` | Measure between two parts: the shortest distance from one to the other, the point on each where it is measured, whether they touch, and the volume they share, which is 0 for parts that fit and above 0 for parts that clash. The document is not changed. | `a`: string, required; `b`: string, required |
| `bill_of_materials` | List the document's parts as a bill of materials: parts placed from one source as one shape are one line with a count, every other part a line of its own. Each line gives its name, count, the parts it counts, one part's volume in mm3, its mass in g when a material or a density is given, and its size before it was placed. | `density`: number; `material`: string |
| `interference` | Check every pair of parts, or of the parts named, for interference: each pair is overlap, with the volume they share and its bounds, touching (they meet but share no volume), or clear. Answers the pairs and how many overlap. | `names`: array of string |
| `render_view` | Render a PNG picture of the document, or of the parts named, from a standard view in one of the window's display modes, so what was built can be seen. The picture comes back inline, and a copy is saved where the user can open it, beside the window's saved document, else in the server's folder, else in Documents\DX-CAD\renders; the answer says its whole path. | `names`: array of string; `view`: one of front, back, left, right, top, bottom, isometric; `mode`: one of shaded_edges, shaded, wireframe, translucent; `width`: integer; `height`: integer; `explode`: number |
| `sheet_base_flange` | Add a sheet metal part: a closed outline on a plane, a sheet's thickness thick, that sheet_flange can bend flanges on and flat_pattern can unfold, with any round holes and rectangular cutouts cut through it. Answers its facts. On a sheet part, give holes and rectangular cutouts with the sheet tools' holes and cutouts, and shape where flanges or returns meet with a corner treatment, rather than cutting: a through cut normal to one face is kept as that face's cutout or hole, a cut across a bend zone or a corner is refused, and any other boolean makes a plain solid that cannot be unfolded. | `name`: string, required; `points`: array of array of number (2) (at least 3), required; `thickness`: number, required; `bend_radius`: number, required; `k_factor`: number; `plane`: string or object; `holes`: array of array of number (3); `cutouts`: array of array of number (4) |
| `sheet_flange` | Bend a flange on one edge of a sheet part's outline, or on the part of it between start_inset and end_inset: a bend of its inside radius, its own bend_radius or the sheet's, then a straight leg with any round holes and rectangular cutouts cut through it, and with relief a bend relief slot beside each inset end. At angle 180 it is an open hem, its leg back over or under the base, refused with a bend radius of 0 or on an edge sharing a corner with another flange unless it is inset at least the thickness at that corner. With return_length, a 90 degree flange gets a second 90 degree bend at the leg's end and a return leg that long, as a channel's lip. With length_from "outside", length runs to the outside mould line, where the base's and the leg's outside faces meet, as a drawing dimensions it; with a return, length runs outside to outside and return_length to the return's outside mould line. Edge n runs from corner n to corner n + 1. Answers its facts. On a sheet part, give holes and rectangular cutouts with the sheet tools' holes and cutouts, and shape where flanges or returns meet with a corner treatment, rather than cutting: a through cut normal to one face is kept as that face's cutout or hole, a cut across a bend zone or a corner is refused, and any other boolean makes a plain solid that cannot be unfolded. | `name`: string, required; `edge`: integer, required; `length`: number, required; `angle`: number; `direction`: one of up, down; `start_inset`: number; `end_inset`: number; `relief`: boolean; `bend_radius`: number; `holes`: array of array of number (3); `cutouts`: array of array of number (4); `return_length`: number; `length_from`: one of leg, outside; `corner_treatment`: one of mitre, square, open, none; `corner_gap`: number |
| `flat_pattern` | Unfold a sheet part and write its flat pattern as a DXF for a laser or a plasma table: the outline on layer CUT, bend lines on BEND, notes on NOTES; or as an SVG when the output ends in .svg, or as a flat solid in STEP when it ends in .step or .stp. Answers the file, the flat's width and height, its bend count and its bend table for the press brake: each bend's number, angle, direction, inside radius, allowance and bend line length; then its cut length, in mm, and its area, in mm², for a quote. | `name`: string, required; `output`: string, required; `force`: boolean |
| `sheet_flat_part` | Add a sheet part's flat pattern as a part of its own: the flat outline extruded by the sheet's thickness on the XY plane from z = 0, with every hole and cutout cut through it. The sheet part stays as it is. Answers its facts. | `name`: string, required; `result`: string, required |
| `sheet_edges` | Read a sheet part's outline edge by edge, to choose where sheet_flange bends one: each edge's number, as sheet_flange takes it, its start and end corners, its length, and the flange on it as its note, such as UP 90 R2, and its straight leg, or null for both when it is free. Answers the sheet's thickness, bend_radius and k_factor and the edges. Changes nothing. | `name`: string, required |
| `linear_pattern` | Copy a part in a row, each copy one step further along than the last. Left alone the copies are new parts, name_2, name_3 and so on; with fuse they are joined into the part; with cut_from they are all cut out of another part. | `name`: string, required; `step`: array of number (3), required; `count`: integer, required; `fuse`: boolean; `cut_from`: string; `keep`: boolean |
| `circular_pattern` | Copy a part in a ring about an axis, the copies spread evenly over the angle. Left alone the copies are new parts, name_2, name_3 and so on; with fuse they are joined into the part; with cut_from they are all cut out of another part: a bolt circle. | `name`: string, required; `point`: array of number (3), required; `direction`: array of number (3), required; `angle`: number; `count`: integer, required; `fuse`: boolean; `cut_from`: string; `keep`: boolean |
| `hollow` | Shell a part to a wall of one thickness, taken from the inside, leaving the faces named open: a box becomes a tray. | `name`: string, required; `thickness`: number, required; `open`: array of array of number (3) (at least 1), required |
| `project_open` | Open a .dxcprt or .dxcasm project file, a part or an assembly (a .dxcad from before them opens too). The document becomes the project's, what was there before is gone, and the history starts again. Answers what describe would. | `path`: string, required |
| `project_save` | Save the document as a .dxcprt or .dxcasm project file: a .dxcprt for one part, a .dxcasm for an assembly. The dxcad window and command line open. It carries the model too, when there is one. | `path`: string, required; `force`: boolean |
| `export` | Write one part to a STEP, STL, 3MF or BREP file, by the path's extension: .step for other CAD, .stl or .3mf for a slicer, .brep for OpenCASCADE; or, ending .dxf or .svg, a drawing of the Sketches the document's model names, one layer each. | `path`: string, required; `name`: string; `force`: boolean |
| `import_part` | Read a part from a STEP or BREP file into the document as a new part, and answer its facts. The file is not changed. | `path`: string, required; `name`: string |
| `drawing` | Draw the document's parts on a drawing sheet and write it as a DXF or a PDF, by the path's extension: the front, top, right and isometric views, hidden edges dashed, at one scale that fits, in the title block with its fields filled, and a parts list. Answers the sheet, the scale, the views and the parts listed. | `path`: string, required; `sheet`: one of A4, A3, A2, A1, ISO-A4-portrait, ISO-A4, ISO-A3, ISO-A2, ISO-A1, ISO-A0, ANSI-A, ANSI-B, ANSI-C, ANSI-D; `fields`: object; `file_name`: string; `force`: boolean |
| `get_model` | The model.py the document carries: the Python that builds its parts, or null. | none |
| `run_model` | Run a model.py, Python source that builds parts with the kernel's functions (make_box, cut, hole, Sketch, ...) and registers each with part("name", shape). The document becomes what it builds, as one undoable step, and carries the source as its model, so the project saved afterwards is parametric. It runs with the user's own permissions. Answers what describe would, with what the model printed as output. | `source`: string, required; `timeout`: number |
| `model_values` | The numbers the model.py is made of: every top-level NAME = value line whose value is a number, a string or a boolean, by name. These are what model_set changes. | none |
| `model_set` | Change some of the model.py's numbers, as model_values lists them, and run it again: the way to make a parametric part longer or its holes wider without writing the model again. One undoable step, and a model that fails with its new numbers leaves everything as it was. It runs the model, with the user's own permissions. Answers what run_model would. | `values`: object, required; `timeout`: number |

<!-- end of generated tools -->

Each tool's arguments are described by the server itself, in the schema
`tools/list` answers, which is what the agent reads. The table above is
generated from those same schemas by `python -m dxcad.docsgen agents`, so
it says what the server says. A tool that was asked
properly and cannot do it, a fillet too large for its part, a name already
taken, answers in words and leaves the document as it was, so the agent can
read why and try something else. A part named that the document does not
have is refused naming the parts it does have.

### The booleans

`fuse`, `cut` and `common` take the same inputs, two parts by name:

- `a`: The part that is kept and changed.
- `b`: The other part, which is taken out of the document afterwards unless keep is true.
- `keep`: Leave b in the document. False when left out.
- `proceed`: Go ahead with a boolean that turns a sheet part into a plain solid, losing its flat pattern; refused without it. False when left out.
- `as`: A name to add the result under, leaving a as it is. Without it the result replaces a.

`a` and `b` are required. To fuse a boss onto a plate, `fuse` with `a` the
plate and `b` the boss; to drill with a cylinder, `cut` with `a` the part and
`b` the cylinder. Both are made first with the tools that add parts, and
their names are the names those tools were given.

On a sheet part, a `cut` that passes cleanly through one flat face, a round
or rectangular prism normal to it and clear of the bends, is kept as that
face's hole or cutout, so the part still unfolds. A cut across a bend zone or
a corner is refused: shape corners with a corner treatment, or give cutouts
on the faces either side. Any other boolean on a sheet part is refused unless
`proceed` is true, since it makes a plain solid with no flat pattern.

The order of the tools in `tools/list` is not fixed: a new tool may be listed
beside the ones it belongs with and move the rest along. A client looks each
tool up by its name, never by its place in the list.

## Without a client

The server is one JSON object a line in and one a line out, so it can be
tried from a shell with nothing but a pipe:

```
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | dxcad serve
```
