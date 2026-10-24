# Plugins

A plugin is a Python package that adds to DX-CAD&trade; without DX-CAD knowing it:
names for model.py, `dxcad` subcommands, tools for the MCP server and actions
in the window. Install it into the same environment as DX-CAD and the window,
the command line and `dxcad serve` all load it when they start.
`dxcad doctor` prints a `plugins` line naming each one loaded and its version,
and the plugin API this DX-CAD has, `plugin API 2`. `dxcad plugins` says
more: for each one, the names, commands, tools and actions it registered, or
why it was skipped (see [cli.md](cli.md#plugins)).

The DX-CAD SDK, the `dxcad-sdk` package built from the repository's `sdk`
folder under Apache 2.0, describes this API as protocols (`dxcad_sdk.plugin`),
types every name a model.py starts with, checks a plugin's declarations with
`dxcad-sdk check PATH`, and carries three example plugins and a starter.

## Declaring one

A plugin declares an entry point in the `dxcad.plugins` group, in its own
pyproject.toml, naming a function that takes a registry:

```toml
[project.entry-points."dxcad.plugins"]
hello = "dxcad_hello:register"
```

The entry point's name, `hello` here, is the plugin's name: its menu and its
toolbar in the window carry it.

## What the registry takes

| Call | What it adds |
| --- | --- |
| `registry.require(version)` | Nothing: it says the plugin needs plugin API `version`, a whole number from 1. A DX-CAD whose plugin API is older skips the plugin, saying "needs plugin API 3, this DX-CAD has 2", and uses nothing it registered. Call it first. |
| `registry.licence_words(name=None)`, `registry.offer_end()`, `registry.trial_end()` | Nothing: plugin API 2 (item 889), so a plugin that calls them says `registry.require(2)`. `licence_words` answers the line DX-CAD shows for an add-on's licence now, by its name, the plugin it installs as or its licence's product id, this plugin's own with no name: "Free until your trial ends on DATE" while the install's own 30-day trial grants it, the licence's line ("Licensed (licence 42, 3 seats); works offline until DATE.") while a licence naming it is active, the words for a licence that could not be checked online in 14 days or a computer clock set back, and else what its commands say while it is locked, "Requires NAME: see LINK". `trial_end()` answers the last day of this install's own 30-day trial (a `datetime.date`; editing locks at 23:59 UK time on it), and `offer_end()`, kept for plugin API 2 now that there is no offer, answers the same. An add-on's About box shows them so it says what Help > Licence says, with no import of `dxcad.licence`, which is private to a plugin. |
| `registry.add_name(name, value)` | A name every model.py starts with, as `part` and `make_box` are. |
| `registry.command(name, help, run, configure=None)` | A subcommand of the command line called `name`: `configure(parser)` adds its arguments to an argparse parser, `run(args)` does it and answers the exit status. |
| `registry.tool(name, description, input_schema, call, reads=False, drawing=False)` | An MCP tool: its arguments are held to `input_schema` first, then `call(document, arguments)` answers what JSON can carry. `reads=True` says it changes nothing. `drawing=True` hands `call` a third argument, the drawing it works on: the drawing tab in front, or the `.dxcdrg` file the call names as `"drawing"` (see [Drawings and model.py](drawing.md)). |
| `registry.action(key, text, run, icon=None, shortcut=None, menu=None, toolbar=True, submenu=None, applies_to=None)` | A window action on the plugin's menu and toolbar: `run(window)` does it. `icon`, the path of an SVG or PNG, is what its toolbar button shows, its text then being the tooltip; a path that is not there skips the plugin. `shortcut` is a key sequence as text, such as `"Ctrl+Shift+W"`; one a built-in action already has, such as Undo's `"Ctrl+Z"`, is left off with one line on stderr, and the action is still added. `menu` is a built-in menu's title without its ampersand, such as `"Sheet Metal"`: the action goes at the end of that menu, after a separator, instead of on the plugin's menu, and stays on the plugin's toolbar; a title no built-in menu has puts it on the plugin's menu with one line on stderr. `toolbar=False` keeps the action off the plugin's toolbar, which holds at most eight commands (the rest go in submenus); `submenu="Cones"` puts it in a submenu of that name on the plugin's menu, made on first use, the submenus standing in the order first named. An action names a built-in `menu` or a `submenu` of the plugin's own, not both. `applies_to` says where the action applies (item 856), some of `"part"`, `"assembly"`, `"drawing"` and `"sketch"` (a sketch in progress), as a tuple such as `("drawing",)`: with another tab in front its menu entry and toolbar button are greyed, their tooltip saying why ("Needs a drawing tab: open a drawing for Sheet Notes", "Open a part or assembly for Weld"), as DX-CAD greys its own commands; `None`, the default, is everywhere, as before, and anything else skips the plugin. |
| `registry.dialog(key, text, fields, run, icon=None, shortcut=None, menu=None, toolbar=True, submenu=None, applies_to=None, steps=None)` | A window action that opens a dialog first. `fields` is a list of `(name, label, default)`: a number default gives a number box, a text default a line of text. Once the dialog is accepted, `run(window, values)` is called with what was given, by name, in one undo step; backed out of, nothing happens. The rest is as `registry.action` takes it. `registry.dialog(..., steps=[...])` gives the dialog its steps, a line each (item 862): F1 in the dialog opens the guide with "Next steps: TEXT (step 1 of N)" over it, as a sheet tool's steps are shown while it waits. |
| `registry.require_entitlement(name, link=None)` | Nothing of its own: it says the plugin needs the entitlement `name`, which `link` says how to get; with no `link` the words carry DX-CAD's own buy link for the add-on, which `registry.buy_link(name=None)` answers: the link DX-CAD last read for the add-on of that name, plugin or product id, this plugin's own with no name (item 845). DX-CAD asks every installed entitlement provider, an entry point in the `dxcad.entitlements` group naming a callable `holds(name)` that answers True or False, whether it is held. Without it the plugin loads locked: its toolbar and menu show, greyed, saying "Requires NAME: see LINK"; its tools are listed and refused with the same words; its model names and kinds of sheet part are not there; and a file using it opens as one whose plugin is not installed does. `dxcad plugins` says each plugin's state: open (it needs nothing), unlocked or locked. The open DX-CAD ships no provider and holds no licensing code, key format or network call. |
| `registry.sheet_kind(name, build, unfold)` | A kind of sheet part, known as `"PLUGIN.NAME"`. A model makes one with `sheet_part("PLUGIN.NAME", ...)`, which calls `build(...)` for a `SheetPart` (its solid, spec, profile and plane, with anything the unfolder needs in `record`). `flat_pattern` hands the part to `unfold(part)`, which answers a `FlatPattern`: the outline, the bends and any holes and cutouts, in the form sheet metal's own flats take. So `dxcad flat` and its `--bends`, `--cut`, `--edges`, `--title` and `--bend-zones`, the DXF, SVG and STEP writers, the mass line and Sheet Metal > Export Flat Pattern all work on it unchanged. A model that uses a kind whose plugin is not installed is refused: "sheet part kind 'PLUGIN.NAME' needs the plugin 'PLUGIN', which is not installed". `flange()` does not add to such a part. |
| `registry.view_kind(name, draw, dxf_image=True)` | A kind of drawing view, known as `"PLUGIN.NAME"`. `draw(document, scale, at, data)` answers the view's polylines, each a list of `(x, y)` in the sheet's millimetres, from the model, the drawing's scale as drawn over true, `at`, where on the sheet the view is placed, and `data`, what the drawing keeps for it. A shaded view answers `(polylines, (png, box))` instead: its picture, the bytes of an 8-bit grey or RGB PNG, not interlaced, filling `box`, `(left, bottom, right, top)` on the sheet; the PDF embeds it as an image and the DXF as an IMAGE entity naming the PNG, which is written beside the DXF. A window action puts one on the drawing in front with `window.add_drawing_view("PLUGIN.NAME", (x, y), data)`, one undo step, and an annotation with `window.add_drawing_annotation("PLUGIN.NAME", view, ref, data)`, `view` a standard view the drawing shows or the index of one of the plugin's views on it, one undo step too; with no drawing tab in front, or no such view, nothing changes, the reason is said on the status bar and the call answers False. Each of these is optional: `draw` may answer `(polylines, texts)`, each text `(x, y, height, words)` as an annotation's, such as a hole table's words or a "SECTION A-A" label, shown on screen, in the PDF and as TEXT in the DXF, or `(polylines, texts, (png, box))`; a `draw` that takes `dpi` is handed None on screen and the export's dots per inch (300) when the drawing is written to a PDF or DXF, so a picture can be made at the resolution it is printed at; `registry.view_kind(name, draw, dxf_image=False)` writes a picture view's lines alone to the DXF, with no IMAGE entity and no PNG beside it. A `draw` that takes `free` is handed where the sheet is free: rectangles `(left, bottom, right, top)` in the sheet's millimetres, largest first, none overlapping another, inside the frame and clear of the title block, the parts list and the standard views with their dimensions, centre lines and labels; one that takes `sheet_name` is handed the sheet's size, such as `"A3"`. So a plugin places its own views and tables where the core's layout leaves room, whatever that layout becomes. A window action reads the size with `window.drawing_sheet_name()`, None when no drawing tab is in front. Without drawing the sheet, `dxcad.plugins.free_area(document, sheet_name)` answers the same rectangles a draw on sheet `sheet_name` would be handed, from the views' outlines with no hidden-line work: `document` is a model's Document, drawn with a drawing's defaults, or a DrawingDocument, drawn with its own settings on that size; so a command that writes a drawing can tell whether its content fits before anything is drawn. `registry.view_kind(name, draw, edit=None, menu=None)` (item 861): `edit(window, record)` is called on a double-click on one of the views or on its label (a view's box holds its words whole), and `menu`, `[(text, call), ...]`, puts an entry on the right-click menu of one for each, `call(window, record)`; `record` is a copy of the view's, `{"kind", "at", "data"}`, and `window.selected_view()` is its `(plugin, index)`, so a scale typed on the view itself is put back with `window.set_drawing_view(plugin, index, data, label="Detail Scale")`. What either raises is said on the status bar. A view's `draw` taking `text_height` is handed the height the drawing letters in (item 868), Drawing properties' Text height or the sheet's own, as an annotation's `draw` is, so a detail view's label follows the drawing's text height; the view is drawn again when it changes. |
| `registry.annotation_kind(name, resolve, draw)` | A kind of annotation, such as a dimension, a balloon or a note, attached to a standard view (front, top, right or iso, the isometric view) by a reference, `ref`, plain data the drawing keeps. Every time the sheet is drawn, `resolve(document, ref)` finds the model point `(x, y, z)` it names again, so the annotation follows the model, or answers None, and the annotation is reported as lost on the status bar; `draw(at, data)` answers `(polylines, texts)` drawn at `at`, the point on the sheet, each text `(x, y, height, words)`. Each of these is optional: `resolve` may answer a list of model points, and `draw(points, data, scale)` is then called with each point's place on the sheet and the view's scale; a `draw` that takes them as keywords is also handed `document`, `scale` and `origin`, the view's origin on the sheet, and `free` and `sheet_name` as a view's draw is, and `outline`, the standard view's box on the sheet, `(left, bottom, right, top)` in mm, or None on a plugin view. `draw` may answer a third item, a dict, where `{"warn": True}` draws the annotation in the window's warning colour on screen only, never in an export. Its polylines may hold `("dimension", kind, p1, p2, line_point, text)` in sheet mm, kind `"linear"` or `"diameter"`: a real dimension, drawn as DX-CAD's own are and written to the DXF as a DIMENSION entity. Each of these is optional too: a `"linear"` entry may take a seventh item, its rotation in degrees, 0 across, 90 up and any other an aligned size along that angle (the DXF's group 50), else it is across or up whichever its points are further apart along; `("dimension", "radius", centre, rim, leader_end, text)` is a radius, written as a radial DIMENSION; `("dimension", "angular", vertex, ray_one, ray_two, arc_point, text)` the angle at `vertex` between the rays through the two points, its arc through `arc_point` and on that side, written as a 3-point angular DIMENSION whose measurement (group 42) is in radians, as AutoCAD keeps it; `("dimension", "ordinate", datum, feature, leader_end, "x" or "y", text)` how far `feature` lies from `datum` along that axis, written as an ordinate DIMENSION; and any entry may end with the position of its text, `(x, y)` in sheet mm, kept as the DXF's group 11 (a linear one gives None for its rotation to keep it across or up). `annotation_kind(..., layer="dimensions")` puts what it draws on the sheet's DIMENSIONS layer, where DX-CAD's own dimensions are, instead of the plugin's. An annotation's `view` may be the index of one of the plugin's views on the drawing; `resolve` is then handed that view's data, `resolve(document, ref, view_data)`, when it takes three, and its points are in the view's own frame from where the view is placed, at the sheet's scale. `annotation_kind(..., handles=..., drag=...)`: `handles(data)` answers named points in the view's plane, shown on the annotation when it is clicked, and dragging one calls `drag(data, name, plane_point)` for the new data, one undo step. A `handles` or a `drag` that takes them as keywords is also handed `document`, `scale` and `origin`, the view's scale and its origin on the sheet, as `draw` is (item 815): a point kept in sheet mm from the view's origin, such as a balloon's ring, is shown at `offset / scale` and a dropped point kept again as `plane_point * scale`, so it lands where it was dropped at any view scale; one that takes the data alone is called as before. A `drag` that cannot stand raises ValueError, KeyError or RuntimeError with its reason: the status bar says "Move Balloon failed: REASON", nothing changes and the handle goes back (item 841). Delete (the key, or Edit > Delete) on the selected annotation of a kind that registers `handles` takes that annotation's record off the plugin's list, one undo step, as `window.delete_annotation()` does: that annotation alone, nothing else on the sheet moves or is arranged again. `annotation_kind(..., edit=fn)`: a double-click on an annotation of the kind calls `fn(window, record)` with a copy of its record, so the plugin opens the dialog it was placed with; `window.edit_annotation()` does the same for the selected one. `annotation_kind(..., title="Balloon")` and `view_kind(..., title="Detail View")` say what Undo and Redo call one of the kind, "Add Balloon", "Move Balloon", "Delete Detail View"; without a title it is the kind's name in words, `hole_table` as "Hole Table", a view kind's ending in "View", and never the kind's own name or a handle's. Annotations lie in a layer of their own over the sheet: adding, dragging, editing or deleting one draws that layer again and nothing under it, and an annotation whose record has not changed is not resolved or drawn again, so `resolve` and `draw` must answer from what they are handed and nothing else. Several are put on as one change with `window.add_drawing_annotations(records)`, each record `{"kind", "view", "ref", "data"}` as `add_drawing_annotation` takes them one at a time: one undo step, named "Add 51 Balloons" or by `label=`, the sheet drawn once, and all or none, so a record naming a view the drawing has not got adds nothing. A `draw` taking the keyword `views` is handed where every view of the sheet is now (item 863), by a standard view's name (`"front"`) or a placed view's sheet name (`"PLUGIN/INDEX"`, the drawing's own added views `"dxcad/INDEX"`), each `{"origin": (x, y), "scale": s, "box": (left, bottom, right, top)}` in the sheet's mm, so a detail's connecting line can run from its circle on the main view to the detail view; a record may name more views than its own under `"views"`, a list of those names, and the annotation is drawn again, handed their new places, whenever its own view or one it names is moved or rescaled. A `draw` taking `text_height` is handed the height the drawing letters in, Drawing properties' Text height, or the sheet's own (2.5 mm at A4, larger on a larger sheet) when it has none. Its polylines may hold `{"points": [(x, y), ...], "style": "thin"}`, the style one of `"thin"`, `"thick"`, `"centre"` and `"hidden"`: a line of the drawing's line types, drawn on screen, in the PDF and in the DXF as a line drawn by hand of that type is (Drawing > Line), on its layer (`LINES`, `LINES_THICK`, `LINES_CENTRE`, `LINES_HIDDEN`) with its weight (0.18 mm, 0.35 mm thick). |
| `registry.sheet_tool(key, text, run)` | A tool on a drawing tab's right-click menu, called `text`. Chosen, the next click on the sheet is its pick: `run(document, pick)` is handed a `Pick`, the point clicked snapped to the nearest drawn point of a view within 2 mm (`at`, `snapped`), the view it is in (`view`) and where that is in the view's own plane, in the model's millimetres (`plane`), with the point clicked itself, before the snap, as `raw`, for a tool that places what it draws where the pointer was (item 844); it answers an annotation, `{"kind", "view", "ref", "data"}`, which goes on the drawing in one undo step, or None for none. `registry.sheet_tool(key, text, run, hover=None, clicks=1)`: the tool waits for `clicks` clicks, Escape backing out the last one, or ending the tool when there is none, and `run(document, picks)` is handed them all as a list when `clicks` is above 1. `registry.sheet_tool(key, text, run, hover=None, drag=True)` is a tool that takes a press, a drag and a release in place of two clicks (item 846): `run(document, picks)` is handed the press and the release as its two picks, and the moves between them go to `hover`, as a cursor's do between two clicks. `registry.sheet_tool(key, text, run, hover=None, drag=True, clicks=1)` is a drag and then one more click (item 854): a drag tool given `clicks` waits for that many clicks after the release, `run(document, picks)` is handed the press, the release and the clicks after, in that order, and `hover` is called throughout; Escape while the button is held, or after the release, takes the whole drag back, and after a click that click, with nothing made until the last. While it waits, `hover(document, picks, pick)` (or `hover(document, pick)` when it takes two) is called as the cursor moves, with the clicks so far and the pick under the cursor, and the polylines it answers, in the sheet's millimetres, are drawn in the highlight colour on screen only, never saved or exported; None draws nothing. A pick in a view also carries the view's `scale` (drawn over true) and `origin` (the sheet point its model origin is drawn at, as an annotation's draw is handed it), so a point `(u, v)` of the view's plane is drawn at `origin + scale * (u, v)`; both are None off every view. It is called off the window's thread, the latest cursor winning, so a slow hover never freezes the window. Each pick's `key` is the last letter key pressed while the tool waits, as `"H"`, or None. `registry.sheet_tool(key, text, run, typed=True)` is a tool that reads what the user types while it waits (item 860): digits, `.` and `:`, Backspace taking one back, are shown on the status bar as they are typed ("Detail: 4:1 - Enter to take it") and handed to the tool with each pick, and each hover's, as the pick's `typed`, `"4:1"`, or None for nothing typed; Enter takes it, and the next key typed starts afresh. Letters reach the tool as `key` either way, and a tool made without `typed` is handed None. `run` may answer `{"view": {"kind", "at", "data"}, "annotation": {...}}`, adding a view and its annotation, such as a section view and its cutting line, as one undo step. A `run` or a `hover` that takes a keyword `drawing` is handed the drawing in front, as a `drawing=True` tool is: `drawing.annotations(plugin)` and `drawing.scale(view)` as they stood when the tool was called, so a tool can snap from the dimensions already on the sheet; what a `run` sets with `drawing.set_annotations` goes on the drawing with the annotation it answers, in the same undo step, and what a `hover` sets is dropped. `registry.sheet_tool(key, text, run, icon=None, toolbar=False, submenu=None)`: the tool is also listed on the plugin's menu, in `submenu` when one is named, and with `toolbar=True` on the plugin's toolbar wearing `icon`, an SVG or PNG; chosen there with a drawing tab in front it starts as from the right-click menu, and with no drawing tab in front it is disabled, the reason as its tooltip. `registry.sheet_tool(..., applies_to=("drawing",))` says where the tool applies (item 865), as `registry.action` takes it, `"drawing"` among the places since the tool picks on a sheet: with another tab in front its menu entry and toolbar button are greyed, their tooltip saying why ("Needs a drawing tab: open a drawing for Linear Dimension"), as an action's are; places without `"drawing"` skip the plugin. Its `key` shares the plugin's action keys: one an action has too is said on stderr and left on the right-click menu alone. `sheet_tool(..., steps=["Click the centre of the detail.", "Click its rim.", "Click where the view goes."])` gives the tool its steps, what the user does once it is chosen, a line each: F1 while the tool waits for its clicks opens the help with "Next steps: NAME (step 2 of 3)", the step of the next click marked and the steps left under it, as DX-CAD's own commands have; `registry.action(..., steps=[...])` gives an action's steps the same way. |
| `registry.drawing_ready(call)` | Work the plugin's tools would do at their first use, done as a drawing opens (item 864): `call(document, drawing)` is made once a drawing tab has opened and drawn its sheet, with the Document the plugin's tools, hovers and annotations are handed later (the same object, its `revision` the same) and the drawing as a sheet tool's run is handed it (`drawing.annotations`, `drawing.scale`), and again whenever the model changes; not when only the annotations do. It runs on the window's thread as part of the opening, so what it keeps, by `document.revision`, is there before the first click: on the engine example (192 parts) and the gearbox (205) the core's own part of a first change, a linear dimension included, is about a tenth of a second (`python -m dxcad.bench --first-changes`), and what is left is what a plugin works out at its first hover. What it raises is logged and said on the status bar, and the drawing opens. |
| `registry.unfolds(owns, command)` | Nothing of its own: it says which parts the plugin unfolds and with which of its commands. `owns(document, name)` answers whether part `name` is one of them, a part the plugin made and has a flat for, and `command` is what its flat command is called on its menu, such as `"Flat Pattern"`. DX-CAD's own Flat Pattern knows only parts made with Base Flange; picked for one of the plugin's, it then says "elbow_2 was made by Fabrication: use Fabrication > Flat Pattern" where it said the part was not a sheet part. |
| `registry.setting(name, title, scope, default=None)` | A setting the plugin keeps, known as `"PLUGIN.NAME"`, and how long it is kept: `scope` is `"document"` (kept in the file with its view, and `default` in a new file or an example), `"session"` (until DX-CAD closes) or `"preference"` (the user's, across starts). `title` is what the user calls it and `default`, plain data, what it is until set. DX-CAD keeps it where the scope says: `window.plugin_setting(plugin, name)` reads it and `window.set_plugin_setting(plugin, name, value)` writes it, a value JSON can carry. Declare every setting you keep, and keep none of the document's anywhere else: a setting that outlives its file is how a section left on came to cut the next model. [Settings and their scope](settings.md) lists DX-CAD's own. |
| `registry.check(name, call)` | A check of a drawing, known as `"PLUGIN.NAME"`: `call(document, drawing_section)` is handed the drawing's model and the plugin's own section of the drawing, `{"views", "annotations", ...}`, and answers lines of text, which the window lists in the Checks panel of Drawing properties while a drawing tab is in front, read again whenever the drawing changes. One that raises is listed as "PLUGIN.NAME failed: ...". |
| `registry.drawing_function(name, call)` | A model.py function that works on a drawing: run for its parts the model's `NAME(*args)` does nothing; run for a drawing of it, `call(drawing, *args)` is called with the drawing being drawn, which can read and set the plugin's annotations and read a view's scale (see [Drawings and model.py](drawing.md)). |

An annotation on the isometric view, `view` `"iso"`, is resolved and drawn as
one on the front, top or right view is: each model point `resolve` answers is
handed to `draw` where the isometric view draws it, with that view's `origin`
and `scale`, so a balloon or a dimension there follows the model too. A
length lies foreshortened in that view's plane, so what a dimension there
says is the plugin's to work out from its model points.
`dxcad.plugins.view_point(view, point)` answers where a model point
`(x, y, z)` lies in a standard view's own plane, `(u, v)` in the model's
millimetres, the frame a `Pick`'s `plane` is in: drawn, it is at
`origin + scale * (u, v)`. With it a sheet tool can tell which model point a
pick in the isometric view is on, where one `(u, v)` is many points in space.

A plugin's tests can start the window (item 815): `dxcad.plugins.open_window()`
answers DX-CAD's main window, shown, the one an action is handed, with the
plugins loaded and no event loop to wait on. A test opens a drawing in it
with `window.open_drawing(path)`, sends the sheet (`window.sheet_view`) the
mouse and the keys, as `QTest` does, lets Qt handle the events and closes
it; it closes with no question, whatever was changed in it. It is offscreen
under `QT_QPA_PLATFORM=offscreen`. Its settings (Recent Files among them),
its recovery files, its log and the channel it listens on are its own, in a
temporary folder, unless `DXCAD_SETTINGS`, `DXCAD_RECOVERY_DIR`,
`DXCAD_LOG_DIR` or `DXCAD_CHANNEL` is set already, so a test never writes
into the user's own DX-CAD.

A plugin's tests can look at a dialog as DX-CAD builds it:
`window.open_dialog(key)` shows the dialog of `registry.dialog(key, ...)` and
answers it, a QDialog, without waiting on it, and accepting or closing it
calls nothing; `window.set_theme("light")` or `"dark"` puts the window, and
so the dialog, in that theme. Run offscreen with `QT_SCALE_FACTOR` set, that
is how to check that a dialog's fields fit and read at 150 and 200 percent.

A dialog with many fields is built on the long dialogs' form (item 797), so
its OK and Cancel are never off the bottom of a small screen:
`from dxcad.plugins import FormDialog`, a QDialog. Its fields are in a scroll
area and its buttons under it; it is as tall as its fields where the screen
has room and never taller than the screen's available height, and only the
height scrolls. Enter accepts and Esc cancels. `add_group(title)` adds a
titled group to the scrolled column and answers its QFormLayout;
`add_field(label, widget, group=None, name=None)` adds a field to a group, or
below what is there, and keeps it in `fields` under `name`;
`set_picture(picture, stretch=0, fields=1)` puts a QPixmap or a widget in a
column beside the fields, where it stays as they scroll; `body` is the
scrolled column itself, a QVBoxLayout, `footer` a QVBoxLayout between the
fields and the buttons for a line saying what is wrong, and `buttons` the
QDialogButtonBox. `reveal(widget)` scrolls a field into view and
`in_view(widget)` says whether it is, for a test. The dialog of
`registry.dialog` is built on it, as Settings and Flange are, so one of
thirty fields fits a 1366 x 768 screen at 150 percent.

Command search (Help > Search Commands) finds every plugin action and sheet
tool by its text, as it finds the built-in commands. `window.commands()`
lists what the search looks through, `(key, text, other names)` for each
command that is shown and can be used now, a plugin's as `"PLUGIN.KEY"`, so a
plugin's test can check that its commands are found; a sheet tool is there
while a drawing tab is in front.

A plugin's SVG icon is drawn as it is in both themes, as the core's own icons
are: View > Theme changes the 3D view's colours, not the toolbars', which keep
the platform's palette, so the core's icons draw their one ink, `#2b3440`, on
the same light toolbar in the light theme and the dark, and an icon drawn in
that ink reads beside them. Give an SVG a `viewBox`, and the window draws it
sharp at 150 and 200 percent; a PNG is scaled up unless it is at least 48
pixels. `dxcad-sdk check` runs that check, the core's own, on each icon a
plugin's actions and sheet tools name, one line per icon.

A drawing keeps what a plugin's views and annotations need in its .dxcdrg,
under the plugin's name (see the format specification), with what they last
drew. Their lines and words go on the sheet on the plugin's own layer,
`PLUGIN_NAME`, so the PDF and DXF exports carry them as vectors. A drawing
whose plugin is not installed, or is locked, opens with what the plugin last
drew shown in its place and a notice on the status bar, "the drawing's views
and annotations made with NAME, not installed; its last drawing is shown".

The `document` a view, annotation, sheet tool or MCP tool is handed also
answers, read only, what DX-CAD's own drawings know of it, so a plugin's
balloons, hole tables, bend-line dimensions and shaded views agree with them:
`document.parts_list()`, the parts list as the drawing numbers it,
`[(item, [part names])]`, the same numbering as the parts list on the sheet
and the bill of materials, following any reordering of the parts;
`document.hole_groups(part, view)`, the part's groups of identical holes that
the view (`"front"`, `"top"`, `"right"`...) looks into, each a list of hole
centres `(x, y)` in the view's plane in mm, in the order DX-CAD's grouped hole
callouts ("4x ⌀6") take them; `document.view_lines(view)`, the visible edges
of standard view `"front"`, `"top"`, `"right"` or `"iso"` as DX-CAD draws
them, each its points `(u, v)` in the view's plane in mm at 1:1, read only
and the same object at every call until `document.revision` changes, so a
tool need not project the model again (None while the window is still
working a large view's lines out behind it), and
`document.view_lines(view, parts=True)`, the same lines in the same order
each with the part it is an edge or an outline of, `((part, points), ...)`,
the part by its name in the document, so which part a region of the view
shows is read off its lines and no ray is cast, and
`document.view_lines(view, parts="all")`, the same lines each with every part
it lies on, `((parts, points), ...)`, `parts` a tuple of names, the part it is
an edge or an outline of first, then each part whose edge or outline is drawn
under it in the view and each part whose face its edge lies on in space, as a
hub's bore lies on its shaft (worked out the first time it is asked for, about
a second on a model of 200 parts, then kept as the rest is);
`document.view_regions(view)`, the regions those visible lines cut the view
into, each with the part seen in it (item 866), `((part, at, loops), ...)`:
`part` the part's name, `at` a point `(u, v)` well inside the region where a
ray from the viewer meets that part first, and `loops` the region's outline
and then the outlines of its holes, each its points `(u, v)` in order, in the
frame of `view_lines`. The part is the one an exact ray at `at` meets first,
so a lens seen inside its bezel, or the plate seen in a nameplate letter's
counter, is named though no line of its own bounds it; of two parts met at
one place, a seal flush in its cap, it is the one the document names first.
A region where nothing is seen, round the view or through a hole, is left
out. It is worked out the first time it is asked for (1.5 to 6 s a view on a
model of 200 parts), then kept, read only and the same object until
`document.revision` changes; None while the view's lines are being worked
out, as `view_lines` answers;
`document.flat_pattern(name)`, the
`FlatPattern` of sheet part `name`, with its bends, or of a flat part made by
`flat_solid(flat_pattern(...))` in that part's own coordinates, or None for a
part that is neither; and `document.colour(name)`, the part's colour as the window
shows it, `(r, g, b)` from 0 to 255, or None for a part with none of its own.

The `window` a plugin's action is handed reaches the drawing tab in front, so commands such as a dimension style, a delete or a balloon view can act on the plugin's own annotations and views: `window.drawing_annotations(plugin)`, the plugin's annotation records, and `window.set_drawing_annotations(plugin, records, label=None)`, which puts a new list in their place as one undo step, called `label` when one is given (`label="Balloon View"` reads "Undo Balloon View" in Edit) and "Change PLUGIN annotations" when not; `window.selected_annotation()`, the record the user last clicked on the sheet, or None; `window.drawing_views(plugin)`, the plugin's views, `{"kind", "at", "data"}`, and `window.set_drawing_view(plugin, index, data, label=None)`, new data for one, one undo step, called `label` when one is given (`label="Detail Scale"` reads "Undo Detail Scale", item 861) and "Change KIND" when not; `window.selected_view()`, the plugin view the user clicked, `(plugin, index)`, or None; `window.drawing_view_scale(view)`, a view's scale as drawn over true, for a standard view by name or a plugin view as `(plugin, index)`; `window.export_drawing(sheet, path)`, which writes a drawing, a .dxcdrg file or a DrawingDocument, to a PDF or DXF as `dxcad drawing` does, with no tab open; and `window.drawing_document()`, the Document the drawing in front is drawn from, the one its annotations' draw is handed (`window.document` may be another part's), or None when no drawing tab is in front; it is the same Document, holding the same shape objects, from call to call until the model changes, and its `revision`, an integer, is a new and larger number after every change to the parts or the model's text, so what a tool worked out from the shapes can be kept by `document.revision` and found again. Three more read the drawing in front as it is drawn, with its own scale, its views' own scales and its moved views, where `free_area(window.drawing_document(), ...)` lays the model out with a drawing's defaults: `window.drawing_free_area()`, the rectangles a draw on that drawing is handed as `free`, `(left, bottom, right, top)` in mm, largest first, clear of the title block, the parts list and the standard views where the drawing puts them; `window.drawing_view_origin(view)`, where the model's origin is drawn in a view of it and the view's scale, `((x, y), scale)` as a `Pick` carries them, for a standard view by name (`"front"`, `"top"`, `"right"`, `"iso"`) or a plugin view as `(plugin, index)`, whose origin is where it is placed, or None for a view the drawing has not got; and `window.drawing_settings()`, a copy of the drawing's own settings: `"sheet"`, `"scale"` as drawn, `"fitted"`, `"views"` (each moved view's offset), `"view_scales"`, `"dimensions"`, `"parts_list"`, `"hidden_off"`, `"font"`, `"text_height"`, `"labels"`, `"columns"`, `"fields"` and `"precision"`, the precision the drawing's overall sizes are held to in mm (1, 0.1 or 0.01, the Dimension precision field of Drawing properties, one undo step per change; a drawing with none set reports the one its sheet draws at). Each answers None when no drawing tab is in front. With a part or assembly tab in front the reading calls answer an empty list or None, and the setting calls change nothing, say so on the status bar and answer False. With a drawing tab in front, `window.set_drawing_annotations` and `window.set_drawing_view` answer True when the drawing already holds what they are handed, with nothing changed and no undo step, so a dialog accepted as it stood is not a failure; False is for no drawing tab in front, a view index the plugin has not got, and a window locked against editing. When the window has been busy for a second, with a plugin's command as with its own, DX-CAD shows a small "Please wait" window over it, kept up a second after the work ends so it never blinks away; a command under a second never shows it. It says the command's own name unless the command has said what it is doing with `window.say_doing("Placing balloons...")`, words that are forgotten when the command ends. Nothing has to be told that a command began or ended. Under `QT_QPA_PLATFORM=offscreen`, as a plugin's own tests run, the window never waits on a message box: `window.open_drawing(path)` and `window.new_drawing(size)` open their tab, and anything refused is logged, written to stderr and put on the status bar instead.

A view a plugin puts on a drawing, by `window.add_drawing_view` or in a
drawing file's plugin section, is a view of the sheet like the standard ones,
with nothing more to register (item 790): a click selects it, as
`window.selected_view()` answers; a drag moves it live, Esc putting it back,
and the release moves its `"at"`, one undo step; and Delete (the key, Edit >
Delete, or Delete View on the sheet's right-click menu) takes it off with its
annotations, one undo step, the annotations of the plugin's later views
keeping theirs as their indices move down one. A standard view is deleted the
same way, with its sizes, centre lines, label and the annotations on it;
deleting the front view, which the top and right views are aligned to, asks
first and unlocks them.

Where the user adds each kind of view, so an add-on's message can name the
place (item 862):

- A standard view, Front, Top, Right, Left, Back, Bottom or Isometric:
  **Drawing > Add View...**, or **right-click on the sheet > Add View...**.
  The user chooses the view, then, where the model has several parts, what it
  is a view of, then clicks where it goes; Esc leaves it. A view taken off is
  put back the same way.
- A new drawing's first views, front, top, right and isometric:
  **File > New Drawing**.
- A plugin's view, such as a detail or a section: its sheet tool, on the
  **right-click menu of the sheet** under the tool's `text`, and on the
  **plugin's own menu** (the menu bar's menu named after the plugin), in its
  `submenu` when it names one, and on the plugin's toolbar with
  `toolbar=True`; or its window action, on the plugin's menu or the built-in
  menu it names with `menu=`. Its own entries are then on the
  **right-click menu of the view** (`registry.view_kind(..., menu=)`, item 861).

A plugin's toolbar is listed in View > Toolbars beside the built-in ones, and
is made once an action or a sheet tool asks to be on it. An
action that makes a part calls `window.add_part(name, shape, statement)`, which
adds the part and writes `statement`, one line of model.py that builds it, at
the end of the model pane, as the window's own tools and the agent door do;
the template gives way to the first part. An action that changes parts the
user picked reads `window.selected_parts()`, their names in the order they
were picked, and calls `window.replace_part(name, shape, statement)`, which
puts `shape` in place of the part's solid and `statement` in place of the
model's statement that builds it, where it stood; both changes are one undo
step, and a part no top-level `part()` builds is refused. Either call takes a
`SheetPart` as `shape` for a part the plugin unfolds (its sheet kind's): the
part's solid goes into the document and the window keeps the record, so Flat
Pattern, Export Flat Pattern and Bend Table know the part's flat at once,
before the model is run again; a part made any other way has its flat once the
model has run, from the sheet parts the run registered. Everything one command
changes, through any number of these calls, is one undo step, and Undo takes
the parts and their lines back together, the model pane byte for byte as it
was, a model with no lines before the command included (item 788); either call
made outside any command, from a timer or a dialog of the plugin's own, is an
undo step of its own. A shape that is empty, or that OCCT's check
(BRepCheck_Analyzer) refuses, is neither added nor written (item 796): either
call answers the reason, says it on the status bar and changes nothing, and
answers None when it did its work. `window.check_shape(shape)` answers the same
reason, or None for a shape that can be a part, so a dialog can ask before it
enables OK. With the plugin installed, its tools
are in the generated table of docs/agents.md and its shortcuts in docs/gui.md's
when those are written again (`python -m dxcad.docsgen agents` and `shortcuts`).

A part or assembly file carries a section for each plugin that made one of its parts,
under the plugin's name: its version, the parts it made and whatever the
plugin keeps in `plugins.section(document, NAME)["data"]`, which must be
something JSON can carry. DX-CAD writes the section as it is and gives it back
on opening, untouched. A file whose plugin is not installed still opens: its
parts are the solids saved with it, marked "made with NAME, not installed" in
the Parts dock and on the status bar, and Run Script is refused with the same
words rather than failing on the first line that needs the plugin.

A window action runs inside one undo step, so one Undo takes back everything
it changed, and one that raises is rolled back and shown in the same box a
built-in refusal is. A tool that raises `ValueError`, `KeyError`,
`RuntimeError` or `OSError` answers the agent with the message, as a
built-in tool does. `dxcad serve --window` lists a plugin's tools too, and a
call to one is carried out by the open window on its own document, one undo
step per call, as a built-in tool's is.

The built-in names, subcommands and tools always win: a plugin's that has the
same name as one of them is left out. A plugin that fails to import or to
register is reported once, on stderr, with what went wrong, and skipped;
everything else loads as usual.

## A minimal plugin

The whole of `dxcad_hello.py`, a module installed beside the entry point
above. It adds a `washer` to the model language, a `hello` subcommand, an MCP
tool `count_parts` and a window action, Add Washer, that puts a washer in the
document.

```python
"""A minimal DX-CAD plugin: one model name, one subcommand, one tool, one action."""

from dxcad import kernel


def washer(outer, inner, thickness):
    """A flat washer, `outer` and `inner` its radii, standing on the XY plane."""
    return kernel.cut(
        kernel.make_cylinder(outer, thickness),
        kernel.make_cylinder(inner, thickness),
    )


def _configure(parser):
    parser.add_argument("name", help="who to greet")


def _hello(args):
    print(f"hello, {args.name}, from a DX-CAD plugin")
    return 0


def _count_parts(document, arguments):
    return {"parts": len(document)}


def _add_washer(window):
    document = window.document
    document.add(document.unique_name("washer"), washer(10.0, 4.0, 2.0))


def register(registry):
    registry.add_name("washer", washer)
    registry.command("hello", "say hello from the example plugin", _hello, _configure)
    registry.tool(
        "count_parts",
        "Count the parts in the document.",
        {"type": "object", "properties": {}, "additionalProperties": False},
        _count_parts,
        reads=True,
    )
    registry.action("add_washer", "Add Washer", _add_washer, shortcut="Ctrl+Shift+W")
```

With it installed, a model.py can say `part("washer", washer(8, 3, 1.5))`,
the `hello` subcommand given a name greets it, `dxcad serve` lists `count_parts`,
and the window has a `hello` menu and toolbar holding Add Washer. The test
suite installs exactly this plugin, from this page, and checks all four.

## The core's own modules

A plugin takes from DX-CAD only `dxcad.plugins` and `dxcad.model`. What
plugins took from the core's own modules has a public name in
`dxcad.plugins` (item 760):

| Name | What it gives |
|---|---|
| `dxcad.plugins.gauges` | The sheet metals and their gauges: `gauges.SHEET_METALS`, each metal's density in g/cm³ by its name, and `gauges.tables()`, `gauges.gauge(material, thickness)`. |
| `run_model(project)` | A project's model.py run again: its parts, `(name, solid)` in order. `project` is a project's path, or a Document. A model that fails raises `ScriptError`, with its line; once the user's licence locks editing it raises `PluginLocked` with the licence's words, while `load_project` stays free. |
| `load_project(path)` | The Document a part (.dxcprt) or assembly (.dxcasm) file holds; `ProjectError` when it cannot be read. |
| `export_drawing(path, out)` | A drawing, a .dxcdrg file or a DrawingDocument, written to `out`, PDF or DXF, as `dxcad drawing` does, with no window and no Qt; the path written. |
| `ScriptError`, `ProjectError` | The errors of the two above. |

Importing `dxcad.gauges`, `dxcad.script`, `dxcad.project` or `dxcad.cli`
still works for one release, with a DeprecationWarning once per plugin
naming what to use instead, and `dxcad-sdk check` warns of it (WARN, which
fails nothing).

## Testing a plugin

A plugin's tests call the installed DX-CAD, which keeps its log, its
settings (the licence and the trial with them), its autosave recovery, its
add-ons and its gauge table outside any document, in the user's own folders.
Set `DXCAD_HOME` to a folder of the test's own and all of them go there
instead, each in a subfolder; nothing is written to the user's folders. The
SDK's template does this in `tests/conftest.py`: copy it into your plugin's
`tests/` folder. `dxcad doctor` prints the folder in use on its `home` line.

### The command sweep

DX-CAD sweeps its own commands in its test suite (item 786), and an add-on
runs the same sweep on its own: `dxcad-sdk sweep NAME`, NAME being the
plugin's entry point name, with DX-CAD installed in the same Python. It runs
`python -m dxcad.gui.sweep --plugin NAME`, which opens each of the plugin's
commands in DX-CAD's window, offscreen, from four states (nothing open, a
part picked, a closed sketch in hand, a sheet part picked), in a process
whose settings, recovery files and window channel are a folder of its own.
Every dialog a command opens is checked on a 1366 x 768 screen at 100, 125
and 150 percent: it fits (`fits 100%`), its OK and Cancel are shown
(`buttons visible`), OK is enabled with the defaults (`accept enabled`), Esc
cancels (`esc cancels`) and Enter accepts (`enter accepts`). It is then
accepted with its defaults, and every part the command adds must be a valid
solid (`valid part`) that the model, run again, builds (`runs again`); a
command that raises fails too (`raises`). Each failure is one line,
`KEY: CHECK: what was found`, and the exit status is 1 when there is one.
`--known FILE` names failures the add-on already knows of, one `KEY: CHECK`
a line with a `#` and the reason after it: those are passed over, and a
listed one that now passes fails the sweep, so the list only shrinks.

## Building against DX-CAD in CI

An add-on's CI installs DX-CAD's compiled core and the SDK from the
pre-release `core-wheels-latest` of DX-CAD's private repository (or
`core-wheels-VERSION` for one version), which DX-CAD's own CI publishes on
each release. It fetches the wheel for its platform with a read-only token
kept as the secret `DXCAD_RELEASE_TOKEN`, with `DXCAD_REPOSITORY` set to the
repository's owner/name that Designmatix gave you access to:

```text
gh release download core-wheels-latest --repo "$DXCAD_REPOSITORY" --pattern "dxcad-*-manylinux*.whl" --pattern "dxcad_sdk-*.whl" --dir wheels
python -m pip install wheels/*.whl
```

with `GH_TOKEN: ${{ secrets.DXCAD_RELEASE_TOKEN }}` in the step's env. The
patterns are `dxcad-*-win_amd64.whl` on Windows and `dxcad-*-macosx*.whl`
on macOS.

## A sheet kind's unfold

`FlatPattern`, `Bend` and `SheetPart` come from `dxcad.model`, and are the
very classes `dxcad.sheetmetal` has, so `flat_solid`, the DXF and SVG writers
and the cut length and area take the flat an unfold builds. A plate with one
leg bent up on its right edge:

```py
from dataclasses import replace

from dxcad.model import Bend, FlatPattern, base_flange, flange

ALLOWANCE = 4.0  # the bend allowance, worked out however the plugin likes


def build_plate(width, depth, leg, spec):
    base = base_flange([(0, 0), (width, 0), (width, depth), (0, depth)], spec)
    return replace(flange(base, 1, leg), record={"width": width, "depth": depth, "leg": leg})


def unfold_plate(part):
    width, depth, leg = (part.record[key] for key in ("width", "depth", "leg"))
    reach = width + ALLOWANCE + leg
    lines = (((width, 0.0), (width, depth)), ((width + ALLOWANCE, 0.0), (width + ALLOWANCE, depth)))
    return FlatPattern(
        ((0.0, 0.0), (reach, 0.0), (reach, depth), (0.0, depth)),
        (Bend(lines, 90.0, "up", part.spec.bend_radius),),
        part.spec,
    )


def register(registry):
    registry.sheet_kind("plate", build_plate, unfold_plate)
```

`dxcad.model.write_flat(flat, path)` writes any `FlatPattern` to a `.dxf` or
a `.svg` as `dxcad flat` writes a sheet part's, with the same layers, units
and notes, and answers the path; another suffix is a ValueError. It is the
module's own call, asked for by name (`from dxcad.model import write_flat`),
and no name a model.py starts with. A nested sheet is one pattern: the sheet
as the outline, each piece's outline and each hole in a piece as `openings`,
all on CUT, and each piece's number as a note on NOTES.

A pattern may also carry `holes`, `cutouts` and `leg_cutouts` (the flanges'
cutouts, each its four corners on the flat); one without `leg_cutouts` is
written as having none. Its optional `notes`, `((x, y, text), ...)` in the
flat's millimetres, are the plugin's own, such as a piece number, a weld gap
or the bevel along an edge: the DXF and SVG writers put each on the NOTES
layer at its point, at the size and in the style of the bend notes. A note
may take a fourth item, its own text height in mm, `(x, y, text, height)`,
such as a piece number large enough to read on a long strip; a three-item
note is the bend notes' 2.5 mm high. A flat with no notes is written as before.

Its optional `cuts` are open cut lines, each a polyline on the flat that is
left open: the DXF writes each as an open polyline on CUT and the SVG as an
open path, and the cut length counts them, while the area and `flat_solid`
leave them out. That is how a nested layout says where its pieces part. Two
pieces cut from one 200 x 50 mm strip, sharing a slanted line:

```py
strip = FlatPattern(
    ((0.0, 0.0), (200.0, 0.0), (200.0, 50.0), (0.0, 50.0)),
    (),
    spec,
    cuts=(((90.0, 0.0), (110.0, 50.0)),),
    notes=((40.0, 25.0, "PIECE 1"), (150.0, 25.0, "PIECE 2")),
)
```

Its optional `openings` are holes of any shape inside the outline, each a
closed polygon on the flat, its first point not repeated: the saddle a branch
pipe leaves in a tee's wall, or a penetration through a header. The DXF
writes each as a closed polyline on CUT and the SVG as a closed path; the cut
length counts its perimeter, and the area, the mass and `flat_solid` take it
off. An opening outside the outline, or crossing or touching it, is refused
with a ValueError saying which and why. A flat without openings is written as
before. A 300 x 200 mm wall with a 60 mm branch's saddle in it, as 48 points:

```py
import math

saddle = tuple(
    (
        150.0 + 30.0 * math.cos(2.0 * math.pi * k / 48),
        100.0 + 30.0 * math.sin(2.0 * math.pi * k / 48)
        + 6.0 * math.cos(4.0 * math.pi * k / 48),
    )
    for k in range(48)
)
wall = FlatPattern(
    ((0.0, 0.0), (300.0, 0.0), (300.0, 200.0), (0.0, 200.0)),
    (),
    spec,
    openings=(saddle,),
)
```
