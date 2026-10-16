# The window

`dxcad gui` opens the viewer: an OpenCASCADE scene on the left, the model.py
in a pane on the right, and the output of the last run under it. Everything
the window does to a document is an edit that can be undone, and everything it
builds it builds through the same kernel the command line uses.

The window is the one part of DX-CAD that needs a display. Every other command
runs on a machine with none.

## Opening it

On nothing, on a project, or on a model.py. These three are the whole of it:

```
dxcad examples bracket
dxcad run bracket.py --output bracket.dxcprt
dxcad gui
dxcad gui bracket.dxcprt
dxcad gui bracket.py
```

`dxcad-gui` opens the same window with no console behind it, which is what a
desktop shortcut points at. Every command here is in [cli.md](cli.md).

A file that cannot be opened is never met with silence (item 803). Started on
one, by any of these names or by a double click in Explorer, DX-CAD brings its
window up with nothing open and a box that names the file, why it cannot be
opened (it does not exist; it is not a DX-CAD project; for a STEP file that
does not read, the STEP reader's own error) and what would work. The same
words go to the log and the output pane, and the exit status is 2 once the
window is shut. A STEP file is not opened as a project: `dxcad import` makes
a project of it, and a model's import_step reads it. With a window already
open, that window says it instead, once. If DX-CAD cannot start at all, a
message box of the system's own says why in one line and where the log is.

When anything keeps the window busy for a second, a large drawing being
drawn, a model being built, an add-on's command, a small "Please wait" window
appears over it with what is being done, and stays a second after the work
ends so it never blinks away; a command that takes under a second never shows
it. While a model builds it has a Stop button, which ends the run with the
document as it was, as Stop on the status bar and Esc do.

## Tabs

Several documents can be open at once, one tab each (item 570). Each tab has
its own parts, model pane, undo history and file name, and the Parts and
History docks, the title bar and the actions follow the tab in front. The
tabs show above the view once there are two; drag one to move it, and
`Ctrl+Tab` and `Ctrl+Shift+Tab` step through them. The button at the
tabs' right, or Window > Tile, shows them side by side instead. Closing the window asks
once for each tab with unsaved changes. With a window open, `dxcad gui FILE`
or a double click on a part, assembly or drawing file hands the file to that window as a tab. An
agent over `dxcad serve --window` works on the tab in front, and each result
names it.

## The menus

One section per menu, in the order the menu bar has them, and one row per
action. A shortcut is written as Qt writes it, so `Ctrl+Shift+S` on Windows
and Linux is Cmd+Shift+S on a Mac; an action with no shortcut has an empty
cell. The test suite reads the menu bar offscreen and holds this list to it,
row for row.

The menus and toolbars follow the tab in front (item 856). A command that
does not apply to it is greyed, not hidden, so the menus keep their shape,
and the pointer over it says why: a Model or Sheet Metal command on a
drawing's tab says "Open a part or assembly for Flange", a Drawing command
on a part's says "Needs a drawing tab: open a drawing for Add View", and a
Sketch tool with no sketch in progress "Start a sketch for Line". Files,
Undo, Redo, Delete, Zoom Window, Measure, the panels, the window and Help
apply on every tab. A command that applies but is greyed for want of
something says what it needs, such as "Fuse: Needs two parts or more". An
add-on's command is greyed the same way where it says it does not apply.

### File

| Action | Shortcut | What it does |
| --- | --- | --- |
| `New Part` | `Ctrl+N` | An empty part in a new tab, with the model pane holding the template a new model starts from. A tab with nothing open is started again instead. It is saved as a part file, `.dxcprt`. |
| `New Assembly` | | An empty assembly in a new tab, saved as an assembly file, `.dxcasm`: the model pane shows how parts are used from their own files with `use()` and placed with `place()`, and the Parts dock opens. |
| `New Drawing` | | A drawing of the saved part or assembly in front, on the default sheet, in a tab of its own, saved as a drawing file, `.dxcdrg`; as `Drawing...` does at its default size. |
| `Open...` | `Ctrl+O` | Open a part, assembly or drawing file (.dxcprt, .dxcasm or .dxcdrg; an older .dxcad or .dxcaddrg opens as one of them) in a tab of its own; a file already open brings its tab forward. Nothing in it is run: a carried model is asked about at the first Run. |
| `Open Recent` | | The last 10 files opened or saved, newest first, each by its name with its full path as a tooltip and numbered 1 to 9 and 0 for the keyboard; kept from one session to the next. Opening or saving a file moves it to the top. A file that is gone is shown in italics, marked (not found); choosing it says so and takes it off the list. Clear Recent empties it, leaving a greyed No recent files. A file opens in a tab, as Open's does. |
| `Close` | | Close the current tab, as its cross does; the last tab is put back as New leaves it: no parts, no model, no name, and any sketch ended. Unsaved changes are asked about first. Greyed while nothing is open. |
| `Save` | `Ctrl+S` | Write the document, and the pane's model with it, back where it came from; in a drawing's tab, the drawing as a .dxcdrg. A file opened as an older .dxcad or .dxcaddrg is saved in its new type beside it, the old file kept. |
| `Save As...` | `Ctrl+Shift+S` | Write the document to another file, which becomes the window's own. |
| `Save Model` | `Ctrl+Shift+M` | Write the pane's text back to the model.py it was opened from, and nothing else. |
| `Export Model...` | | Write the pane's text to a new .py file, which the window then follows. |
| `Import Model...` | | Read a model.py into the pane, leaving the document as it is until the next Run. |
| `Export Drawing...` | | In a drawing's tab, write its sheet as a PDF or a DXF, as `dxcad drawing` does. Otherwise write the sketch being drawn, or else every Sketch the model names, as a DXF or an SVG drawing by the extension given, in millimetres, one layer or group per sketch: lines, arcs, circles, ellipses and splines each written as themselves. |
| `Export Parts...` | | Write the picked parts, or every part when none is picked, to one STEP, STL, 3MF or BREP file, by the filter chosen or the name's ending, as `dxcad export` writes them; a 3MF keeps each part a named object. Greyed with no part, hidden in 2D drafting. |
| `Drawing...` | | Make a drawing of the saved project in a tab of its own, on a sheet asked for, A4 to A1 or one of the ten ISO and ANSI sheets, as `dxcad drawing` draws one: the front, top, right and isometric views with hidden edges dashed, at one scale that fits, in the title block with the project, file, date, scale and sheet size filled in, and the bill of materials as a parts list. Each hole a view sees round has its centre lines. The drawing is a document of its own: drag a view to move it, the view and its sizes and label following the pointer while it moves, one undo entry when it is let go and Esc putting it back mid-drag; the top and right views stay in line with the front, moving with it, the top only up and down and the right only sideways, unless Unlock Alignment (on the view's right-click menu, or In line with the front view in Drawing properties) lets one move freely, Lock Alignment putting it back in line; right-click a view to show or hide its dashed hidden lines, and right-click the sheet for its scale, its title block fields and whether the dimensions and the parts list are shown, each one undo entry. While a drawing's tab is in front, the left dock shows Drawing properties: the sheet's size, its Title Block... and the parts list's columns, ticked and dragged into order (Item, Part number, Description, Material, Qty and Rev by default, Size and Mass to be had; the description and material are a part's own description and material properties when it has them), remembered for new drawings and for the bill's Save CSV..., and for the view clicked on the sheet its label and hidden lines. The scale is two number fields, 1 : N or N : 1 with any positive numbers (1 : 25, 1 : 7.5, 2 : 1), the standard ratios offered beside them and To fit as a button; it is applied as it is typed, after a short pause and without Enter, the title block following, and a field that is not a number above 0 is marked red and changes nothing. With a view clicked, the scale typed is that view's own: it alone is drawn at it, with its centre lines and hole callouts, its label says it ("TOP SCALE 1 : 10"), and the title block keeps the sheet's; To fit gives it the sheet's scale again. Save writes it as a .dxcdrg, which holds the project's path and no geometry, so the sheet is drawn again from the project whenever the drawing is opened or its tab comes forward, and the status bar says so; a project that is gone is named by its path. Export Drawing writes it as a PDF or DXF. A project not yet saved is asked to be saved first. Greyed with no part, hidden in 2D drafting. |
| `Send to Slicer` | | Write the picked entry, or every entry when none is picked, to a 3MF and open it in the slicer, which is asked for once and remembered. |
| `Where Used...` | | On a saved file: the assemblies and drawings in a folder chosen, and every folder below it, that use this file, each with how many copies it holds, as `dxcad where-used` lists them. Every part keeps a stable id through renames, so an assembly that uses a part by its old name still finds it, saying the new name in the model's output. |
| `Title Block...` | | The fields a person fills in once for every drawing: company, drawn by, checked by, material, finish, general tolerance, drawing number and revision; and the font the drawing is lettered in, the bundled DejaVuSans (the default) or any TrueType font the system has, with the height of its dimensions, labels and fields, 2.5, 3.5, 5 or 7 mm. Kept from one session to the next and used by every sheet File > Drawing makes. |
| `Settings...` | | Settings, in groups. Mode, the first, is 2D drafting or 3D modelling, 3D modelling at the start: 2D drafting hides every action that acts on a solid (Extrude, Revolve, Edit > Mirror's part option, Sketch on Face, the printability actions and Send to Slicer) and names itself in the title, and 3D modelling shows everything. The mode changes the window only, not the kernel, the command line or the agent door, and is remembered between runs. View, the second, holds Show Planes; Recovery, the minutes between keeps of the unsaved tabs; Parts, the Default material: what a part with no material of its own is made of, mild steel as shipped, which the Parts dock and the Bill of Materials mark "(default)" (a sheet part is its spec's metal); Updates, Check for updates at start, off as shipped (Help > Check for Updates). On macOS it is under the application menu. Controls (item 686) is DX-CAD's own or Classic CAD controls (middle-button orbit): under the second the middle button rotates, Ctrl+middle pans and Shift+middle and the wheel zoom, the left button only picks, `Ctrl+1` to `Ctrl+7` are Front, Back, Left, Right, Top, Bottom and Iso, `Ctrl+8` Normal To, and in the 3D view `F` fits, `Space` shows the View Selector and `S` the Shortcut Bar. The first start asks "Used to another CAD program?" once. |
| `Quit` | | Close the window, asking first when there is an unsaved edit. |

### Edit

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Undo` | `Ctrl+Z` | Take back the last edit to the document, the model pane following it. |
| `Redo` | `Ctrl+Y` | Put back the last edit that was undone. |
| `Rename...` | | Give the picked entry another name, which the model is rewritten to match. A part made in a loop or a helper is renamed by a `rename()` statement after the parts. |
| `Duplicate` | | A copy of the picked entry, under a name of its own, set its own width along x and left picked. |
| `Move...` | | Move the picked part by dragging it in the view: after Move, press and drag, and the part follows the pointer in the plane of the screen, drawn where it would go with how far beside the pointer; let go and it is put there, one undo step, its line in the model wrapped in `translate`. Hold `X`, `Y` or `Z` to keep the drag to that axis of the model. Type a number for the distance instead, along the axis held or the way the drag is going, and `Enter` puts the part there. `Esc` leaves it where it was. A part held by mates moves only along what they leave it free to do, on its face or along its axis; where they leave nothing it does not move, and the status bar names the mate that holds it. |
| `Mirror...` | | Add the picked entry mirrored in the XY, XZ or YZ plane, or in the picked face when one planar face is picked, as a part of its own after the original, writing `mirror` into the model. |
| `Delete` | `Del` | Take the picked entries out of the document. |

### View

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Fit` | | Frame everything the document holds. |
| `Zoom Window` | `W` | Drag a rectangle in the 3D view and it zooms to fit it, keeping the orientation; on a drawing's sheet the sheet does the same. Esc lets the rectangle go, and a click without a drag does nothing. Also on the View toolbar. |
| `Measure` | | Measure by picking, in the 3D view, in a sketch being drawn (its own lines can be picked) and on a drawing's sheet, where a view's scale gives the model's sizes. It stays on until Esc. One pick: an edge's length; a circle's or an arc's radius and diameter; a face's area; a point's place. Two picks: the least distance between them with its dX, dY and dZ, the distance between their centres where both are circles or arcs, and the angle between two straight edges or flat faces. A third click starts again. A pick snaps to a vertex, the middle of an edge or the centre of a circle or an arc of what is under the pointer, with a marker there before the click. The status bar says what to pick ("Measure: pick a point, edge or face - Esc to finish") and then each measurement on a line ("Distance 60.000 mm  dX 60.000  dY 0  dZ 0"). The measurement is said by the picks and in the Measure panel, which opens on the left as a tab over the parts' properties and shuts when Measure ends; its Copy puts it on the clipboard. Sizes are in millimetres, to three decimals or a drawing's own. The button stays pressed while Measure is on, and pressing it again ends it. Nothing is added to the model, and no tolerance is checked. Also on the View toolbar. |
| `Fit Sheet` | | On a drawing tab, show the whole sheet again. The sheet also zooms at the cursor with the wheel and pans with a middle drag, and keeps its zoom when it is drawn again. |
| `Front` | | Look along +Y. |
| `Back` | | Look along -Y. |
| `Left` | | Look along +X. |
| `Right` | | Look along -X. |
| `Top` | | Look down from +Z. |
| `Bottom` | | Look up from -Z. |
| `Iso` | | The three-quarter view a part is usually drawn in. |
| `Normal To` | | Look square at the picked planar face, from the side it faces; with none picked the status bar says to pick one. `Ctrl+8` under the classic CAD controls. |
| `View Selector` | | A pop-up of the seven views and Normal To at the cursor; `Space` in the 3D view under the classic CAD controls. |
| `Shortcut Bar` | | A pop-up at the cursor of the eight commands used most this session, most first, made up from Save, Undo, Redo, Fit, Iso, Run Script, Mate and Duplicate; `S` in the 3D view under the classic CAD controls. |
| `Show Planes` | | Show or hide the three principal planes, XY, XZ and YZ: large, very faint squares about the origin, each tinted as the triad axis that stands out of it, the plane being sketched on a little stronger. Each fades as the view turns it edge on, over about a fifth of a second, and is not drawn at all edge on. Hidden, the plane a sketch is open on still shows. Also on the view's right-click menu and in File > Settings; remembered between runs, on at the first. |
| `Explode...` | | Draw the parts moved apart for an exploded view: each away from the assembly's centre of mass by the factor asked times its distance from it, 0 being assembled. Only the drawing moves; picking, measuring and every edit act on the real parts, and a click on a part as it is drawn picks it. Hidden in 2D drafting. |
| `Hide` | `H` | Hide the picked parts: they are not drawn and a click goes through them. Their rows in the Parts dock stay, greyed, with their eye unticked; the eye ticks or unticks one part, and the dock's right-click menu has Hide or Show for the part under it, Hide Others and Show All. Also on the view's right-click menu. Hiding is a view's state: nothing is written into the model, no undo step is made, and the file keeps the parts hidden. |
| `Show` | | Show the picked hidden parts again, a part picked from its greyed row in the Parts dock. |
| `Hide Others` | | Hide every part but the picked ones. Also on the view's right-click menu. |
| `Show All` | `Shift+H` | Show every hidden part again. Also on the view's and the Parts dock's right-click menus. |
| `Section View` | | Cut the view with a plane, XY, XZ or YZ through the parts' middle or a picked face's plane, also on the Display toolbar: the side beyond the plane is not drawn and the cut faces are capped, hatched in each part's colour. Picking and measuring work on the cut view. Only the view changes, never the model; Esc or Section View again ends it. While it is on, a banner across the top of the view says so, with Turn off, and the cutting plane is drawn faintly; hidden parts and an exploded view are said the same way. The section is the document's: it stays with its file, a new file and an example start without one, and a file saved with one opens with it and its banner ([Settings and their scope](settings.md)). |
| `Section Offset...` | | Move the cutting plane along its normal by the distance typed, from where it started. |
| `Flip Section` | | Show the other side of the cut, the plane where it is. |
| `Continuous Orbit` | `Ctrl+Shift+O` | While ticked, also on the Display toolbar, a drag let go keeps the view turning the way and as fast as it was dragged, until a click, Esc or any view command. The model is not rebuilt. |
| `Turntable...` | | Spin the view steadily about the vertical axis, slow, medium or fast, for a presentation or a recording; untick, click, Esc or a view command stops it. Settings > View > Stop spinning when DX-CAD loses focus, on at first, stops either when another window takes the focus. |
| `Turn the Model After a Run` | | Ticked at first. When Run Script (F5), an Assistant turn or a run of calls from Claude Desktop has built parts and ended without error, the view is fitted to everything, at the angle it is at, and then turned at the turntable's slow speed to show the model off; a press, the wheel or any key in the view stops it and leaves the view where it is, and does nothing else. Unticked, the view is only fitted. A run on change, made while you are at something else, fits and never turns; a run that fails, or that changes no part, leaves the view alone. |
| `Shaded with Edges` | | Draw every part shaded with its face boundaries outlined. The mode at the start. |
| `Shaded` | | Draw every part shaded, without its edges. |
| `Wireframe` | | Draw every part as its edges alone. |
| `Translucent` | | Draw every part shaded with edges at about half opacity, so what is inside can be seen. |
| `Theme` | | Light or Dark, switched at once and remembered between runs; light at the first. Light grades the background from white down to a pale grey-blue and draws a part with no colour of its own in steel blue-grey, outlined in near black; Dark grades from slate to near black and draws parts in pale blue-grey, outlined in near white. The sketch being drawn and its dimensions take a colour that reads on each. `dxcad render --theme` draws in either. |
| `Script` | | Show or hide the model pane. |
| `Output` | | Show or hide the output pane under it. |
| `Parts` | | Show or hide the Parts dock on the left: the document's parts in model.py's order, a sub-assembly's parts listed under it as a tree, each with the operation that made it (extrude, revolve, fuse, place, hole...) and its placement when it was placed. Clicking a part picks it and puts the model pane's cursor on its statement, and a pick in the view marks its row. Under the list, the picked part's properties: its name (edit it to rename the part, as Rename does), volume, bounding box, a sheet part's flat size (its flat pattern's bounding rectangle, X by Y in mm; item 792), its material (a sheet part's spec's metal, else the Default material from Settings, marked "(default)"; choosing another here sets the default), its mass in that material, its colour (click the swatch to choose one: it is written into the part's statement as `color=`, one undo entry, and the view draws the part in it), and the file a placed or used part came from, with Open Source File to open it in a tab (item 576). When a file the model uses with `use()` is saved, here or elsewhere, the model runs again and the status bar says so. The list is read again from the model after every change and is never edited on its own. Open at the first run; the choice is remembered. |
| `History` | | Show or hide the History tab beside Parts: every edit the undo history holds, oldest first, named as Undo and Redo name it ("Extrude sketch 5.0", "Fuse a, b", "Rename b to lid", "Pattern a 5 x 60"), under a Start row, the current one marked and the ones waiting to be redone greyed. Clicking an earlier entry undoes back to it and a later one redoes to it, step by step as Undo and Redo would. While a sketch is open its steps follow, and only they can be clicked. Open at the first run; the choice is remembered. |
| `Feature Tree` | | Open or close the Feature Tree dock: each part in the order the model builds it, and beneath it its features, the calls of the statement that makes it, innermost first, then its sketches and its mates in the model's order. A click on a row picks the part and puts the model pane on that row's line. Nothing in the tree is dragged or re-ordered: the order of mates changes only by editing the model. Closed until opened. |
| `Assistant` | `Ctrl+Shift+A` | Show or hide the Assistant dock, along the bottom of the 3D view until it is moved (after an update from a version that kept it down the side it is moved to the bottom once, and then stays where it is put), "Assistant (powered by Claude)", also on the Display toolbar: type a request and Claude builds or changes the document in front with DX-CAD's own tools, each step shown in the chat, written into the model and one Undo, a render shown inline. It uses your own Anthropic API key (Set Key), kept encrypted for you by Windows; nothing is sent until you enable it, and the first use says what is sent (PRIVACY.md). While a turn runs, an hourglass drawn as a wireframe turns a quarter between steps (still when Windows' animations are off), a bar shows the steps done over the steps Claude planned, and a line says what is happening now, also on the status bar while the dock is shut. Stop ends a turn; the tokens each turn used show under the chat; Settings > Assistant chooses the provider (your own Anthropic key; OpenAI; Azure OpenAI, a deployment in your company's own tenant; Google Gemini; an OpenAI-compatible endpoint, such as a company gateway or a local model under Ollama or LM Studio, which needs no key; or the DX-CAD account), its model (for Azure OpenAI the deployment's name) and its address; the dock's title names the provider, keys are kept per provider, each provider's note on what it is sent shows the first time it is used, and switching keeps the chat. Each document has its own chat. Asked to change a part by its name ("add returns to sheet"), an answer that builds the part again under a new name where the part is asks first, with nothing written yet, whether to change the part or make a copy: Yes changes the part itself, its solid and its line in the model, and No keeps it and places the new part beside it, 20 mm clear, named as a copy; a request that asks for a copy in so many words gets the copy without the question. Either way the answer is one Undo. |
| `Start Page` | | Bring back the start page in the view's place: New, Open, the recent files, the launch examples as pictures (one click opens an example as a new unsaved tab, "NAME (example)", and builds it; nothing is written until Save, which starts in Documents\DX-CAD and puts any file the example reads beside it), a link to these docs, and Connect Claude Desktop, which links Claude Desktop to this copy of DX-CAD in one click: with no DX-CAD in Claude Desktop's settings it writes this one, driving the open window, as `dxcad serve --install` does, says "Connected to Claude Desktop." and offers Restart Claude Desktop now, which closes Claude Desktop and opens it again once you have said yes; with this copy's already there it says "Connected to Claude Desktop." and nothing else; with another copy of DX-CAD there (an old environment, another install) it asks one question, "Claude Desktop is linked to another copy of DX-CAD. Link it to this one?", with Link to this copy and Keep, and keeps the old settings beside the new; and with no Claude Desktop on the machine it says so, with where to get it, and writes nothing. The Python with a console (`python.exe`) and the one without (`pythonw.exe`) of one folder are one copy, and the one written is always the first, whichever started the window. The page is up when DX-CAD starts with nothing open and when the last tab closes, and gives way the moment a document opens. |
| `Toolbars` | | Show or hide each of the six toolbars: View (Fit, Zoom Window, Measure and the seven views), Display (the four modes, Section View, Continuous Orbit and the Assistant), Edit (Undo, Redo, Rename, Duplicate, Delete), Sketch (the drawing tools, then the sketch actions), Operations (Run Script, Extrude, Revolve, Fuse, Cut, Common, Pattern) and Sheet Metal (Base Flange, Flange, Export Flat Pattern, Show Flat Pattern). The same list is on the right-click menu of any toolbar; the choice is remembered between runs. When the window is too narrow for them in one row, the toolbars wrap to a second. |
| `Reset Layout` | | Put every dock back where a fresh install has it: the model pane on the right, the output pane and the Assistant under it along the bottom, Parts, History and the drawing's properties as tabs on the left with the Feature Tree under them, none floating. Which docks are open stays as it is. The Assistant's remembered place and height are forgotten, so it opens along the bottom at the next start too. |

### Model

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Run Script` | `F5` | Run the pane's model and bring the document level with what it builds. A model that fails is shown in the pane, not in a box: its line marked in the margin and underlined, the cursor put on it, what went wrong in plain words in a strip under the pane (Copy Details copies the whole error, its kind and its trace), and "model.py line N: ..." on the status bar. The next good run clears it. A build that takes more than half a second shows the busy cursor and counts on the status bar ("Building model.py... 3 s, Esc to stop"), and then says how long it took. While it builds the window takes nothing but Stop: the view, the Parts list, the menus, the toolbars and the editor take no clicks and no keys, and none is kept for after. Stop, a button on the status bar, and `Esc` end the run at the model's next line with the document as it was before it; a run on change and an Assistant turn are held and stopped the same way, the turn as its own Stop ends it. |
| `Run on Change` | | Keep running it whenever the file on disk changes, for an editor in another window. |
| `No Time Limit` | | Let a run take as long as it likes, instead of the window's minute. |
| `Check Model` | | Run the model and say what it would change, without changing anything. |
| `Show in Script` | | Put the cursor on the line of the model that built the picked entry. |
| `Adopt Parts` | | Write every part the model does not build to a file beside the project, and add the line that reads it back. |
| `Save to Its Own File` | | On an assembly, with one part picked that the assembly's own model builds (a virtual part): write it as a part file, NAME.dxcprt, beside the assembly, and replace its statement in the model with `place(NAME, use("NAME.dxcprt", part=NAME))`, so the assembly uses it from there, where it was; one Undo takes the statement back. Also on the view's right-click menu while it applies. An assembly not yet saved is asked to be saved first. |
| `Fuse` | | Make the picked parts (two or more; Ctrl+click adds one) one new part, `fuse` by name. The inputs stay in the model as plain variables the new part's line is built from. Also on the Operations toolbar; hidden in 2D drafting. |
| `Cut` | | As Fuse, taking the other picked parts away from the first picked. |
| `Common` | | As Fuse, keeping only where the picked parts overlap; parts that do not meet are refused. |
| `Pattern...` | | Repeat the one picked part as one new part, `pattern` by name: linear (along X, Y or Z, how many, how far apart), circular (about X, Y or Z through the origin, how many, over what angle) or grid (how many along X and along Y, how far apart each way). The original stays in the model as a plain variable the pattern's line is built from. A count below 2 is refused. Hidden in 2D drafting. |
| `Pattern Feature...` | | Repeat the picked part's drilled feature, a `hole`, `countersink` or `counterbore` whose centre the model gives as `world=` numbers, across the same part, asked as Pattern... asks. The model's line becomes the one drill given every position, and the part is rebuilt. Places off the face or overlapping each other are refused with nothing cut. Hidden in 2D drafting. A part extruded from a Sketch works too when a circle inside its outline is the hole: the copies are written into that sketch as circles and the part is rebuilt; a circular pattern turns about the centre of another circle or arc of the sketch, the outline's by default, or a centre typed, and copies that would leave the outline or overlap are refused before anything is written. |
| `Text...` | | Letters as a solid, `text3d` by name: the text, the bundled DejaVuSans (the default) or a font of the system's, the height of its capitals and its depth; with a planar face picked, raised on it or sunk its depth into it and cut, the part changing in place, and with nothing picked a part of its own on the XY, XZ or YZ plane. One undo entry. A font that is not found is refused. |
| `Mate...` | | With two faces picked, the first on the part to move and the second on a part placed before it, place the one against the other: coincident, concentric (a hole's or a cylinder's wall picked), a distance or an angle. Writes `mate` into the model and runs it, as one undo entry; a mate the parts cannot meet with the mates before it is refused. The Parts dock's Mates row says what freedom a mated part has left. |
| `Suggest Mates...` | | With a part picked, list the mates its features allow against the parts near it, best first: a cylinder to a hole it fits as concentric, opposed faces as coincident and as distance with the measured gap. Picking a row shows where the part would go. Check the ones to add and Accept Checked, or Accept All; each is written as its own `mate` and undo entry, and nothing is added without the accept. Ranked by how often you accepted the same kind of pair before. Moving a part near another says on the status bar that mates are suggested. |
| `Printability` | | Say whether the picked entry will print: its mass, its overhangs and its thinnest wall, in a box and in the output pane. |
| `Show Overhangs` | | Tick to colour the picked entry's overhanging faces in the view; picking something else, or unticking, takes them down. A Run, undo or edit that changes the entry's shape colours the new faces. |
| `Printing Material...` | | Choose the filament the report assumes: PLA, PETG, ABS, ASA or TPU. PLA to begin with. |
| `Bill of Materials...` | | List the parts as `dxcad bom` does: parts a model placed from one source as one shape are one line with a count, every other part a line of its own, with volume, mass in the printing material and size. Save CSV... writes what `dxcad bom --csv` prints. Hidden in 2D drafting. |
| `Check Interference...` | | Check every pair of parts as `dxcad interference` does, list the pairs that overlap with the volume they share, and show each overlap in red in the view until the dialog is closed. Hidden in 2D drafting. |

### Sketch

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Sketch on Face` | | Start a sketch on the picked planar face. |
| `Sketch on XY` | | Start a sketch on the XY plane. |
| `Sketch on XZ` | | Start a sketch on the XZ plane. |
| `Sketch on YZ` | | Start a sketch on the YZ plane. |
| `Line` | | The drawing tool a sketch starts in: each click puts a point down, joined to the one before. Escape comes back to it from any tool, ending the figure being drawn. Return, a double click, Finish Figure or choosing a tool that draws a figure of its own ends the chain where it is, and the next click starts a new figure: a sketch holds many figures, open or closed. While a sketch is open the status bar reads where the pointer is on the sketch plane in millimetres, the snap firing there, and the measurement the live tool is waiting for: a line's length and angle, a rectangle's width and height, a circle's radius, an arc's radius and included angle, a polygon's across-flats and side, a slot's length and width, an ellipse's two half-axes. Typing a number instead of clicking opens a small entry beside the pointer for those measurements: Tab moves between the two, Return puts the point down at exactly that size and Escape goes back to clicking; lengths are millimetres and angles degrees. As each figure is finished the script pane shows it, written as `sketch = (Sketch(...)...)` after the model that was there, so the numbers can be read while drawing; Cancel Sketch takes the line out again, an extrude or revolve writes the part in its place, and typing in the pane while drawing leaves it to you. Anything the sketch refuses, a click it cannot draw, a corner too small for its fillet, an offset the shape cannot take, a constraint the others leave no room for, is shown in a box that says what was asked, why not and what would work, and the same words go to the output pane; the sketch is left as it was. The live tool is checked on the Sketch toolbar and named on the status bar, and a line from the last point follows the pointer. |
| `Rectangle` | | Two clicks, one corner and then the opposite one, put down an axis-aligned rectangle as four points in a closed loop, ready to constrain or extrude. The outline follows the pointer after the first corner. It is a figure of its own, drawn beside whatever else the sketch holds. |
| `Circle` | | Two clicks, the centre and then a point on the rim, put down a real circle, written into the model as one `circle` call. The rim follows the pointer after the centre, and the status bar reads the live radius. Circles are drawn beside whatever else is there: inside a closed outline they are holes, and on their own the largest is the outline. A rim on the centre draws nothing and says so. |
| `Arc` | | A three-point arc in the chain being drawn: its start (the last point, or a first click on an empty sketch), its end, then a point on the arc. Three points in line draw a straight segment and say so. An end on the first point closes the loop. |
| `Centre Arc` | | An arc about a centre, going anticlockwise: the centre, the start (the last point, or a click on an empty sketch), then the end, which lands on the circle towards the click. The status bar reads the radius. An end on the first point closes the loop. |
| `Polygon` | | A regular polygon: the centre, then a corner on the circle around it. The number of sides, 3 to 24, is asked every time the tool is chosen, the last answer offered (6 the first time). The corners are points in a closed loop, ready to constrain or extrude. A figure of its own, beside the others. |
| `Slot` | | Two centres, then a click as far from the line through them as half the slot is wide: two parallel sides capped by half circles, written into the model as one `slot` call. The status bar reads the width. A figure of its own, beside the others. |
| `Ellipse` | | The centre, the end of the major axis, then a click as far from that axis as the minor half-axis is long: an exact ellipse, written into the model as one `ellipse` call. The status bar reads each half-axis as it is drawn. A figure of its own, beside the others. |
| `Spline` | | A smooth curve through every point clicked, ended by a double click or Return. It is left open: Close Sketch joins its last point to its first with a straight line, when that is wanted. It needs three points at least; with fewer, Return says so and draws nothing. A figure of its own, beside the others. |
| `Done with Line` | | Leave the live tool, as Escape does: the figure being drawn is ended where it is and Line is live again; Trim and Break are left without ending anything. The entry is named for the live tool ("Done with Break") and is first on the right-click menu while a sketch is open, where Cancel Sketch is last. Return does the same when no figure is under way; part way through one it ends the figure, as it always has. The status bar ends with what the live tool waits for and "Esc or Enter when done", and once figures are set aside it counts them and all their points ("7 figures, 14 points"). |
| `Finish Figure` | | End the figure being drawn where it is, open, and leave the sketch open for the next, as Return and a double click do; it is also on the right-click menu. Extrude and Revolve take every closed figure: side by side they are separate solids, and one inside another is a hole. |
| `Close Sketch` | | Close the figure being drawn, so it can be extruded or revolved; the figures finished before it are left as they were. |
| `Cancel Sketch` | | Throw the sketch away and leave the document as it was. |
| `Horizontal...` | | Make the segment last under the cursor horizontal, or one asked for by number from 0 when the cursor was over none or has not moved over the view since the last constraint action; the points move as little as they can. |
| `Vertical...` | | Make a segment vertical, the one under the cursor or one asked for by number. |
| `Coincident...` | | Put two points in the same place: the first is the one under the cursor, or asked for by number like the second. |
| `Dimension...` | | Make a segment, the one under the cursor or one asked for by number, the length asked for. A constraint that cannot be met with the others is said in the status bar and changes nothing. |
| `Constraints...` | | List the sketch's constraints and remove the one chosen; the points stay where they are. |
| `Radius...` | | Fix a circle's radius, the circle asked for by number from 0 in the order drawn; its centre stays where it is. On a sketch with arcs, a circle or an arc is chosen from a list, an arc named by its segment's number, and the arc's ends stay on their neighbours. |
| `Diameter...` | | Fix a circle's diameter, as Radius does. |
| `Tangent...` | | Make a segment's line, the one under the cursor or one asked for by number, touch a circle asked for by number. On a sketch with arcs, a straight segment or a circle is chosen, then a circle or an arc, so a line or a circle can touch an arc. |
| `Concentric...` | | Give two circles, asked for by number, one centre; on a sketch with arcs, any two of its circles and arcs, chosen from a list. |
| `Equal...` | | Make two segments the same length, or two circles or two arcs the same size, each chosen from a list. A constraint on circles or arcs that cannot be met is said in the status bar and changes nothing. |
| `Fillet Corner...` | | Round a corner where two straight segments meet, the point under the cursor or one asked for by number, with an arc. The radius is asked every time, the last one offered (2.0 the first time). One too large for the corner is said in the status bar and changes nothing. |
| `Chamfer Corner...` | | Cut a corner straight across, the same distance back along each side, picked as Fillet Corner picks. The distance is asked every time, the last one offered (2.0 the first time). |
| `Offset...` | | Replace the closed sketch with its offset by a distance that is asked for, outwards, or inwards when negative, so a wall, a clearance or a gasket comes from a shape already drawn. Corners going outwards are rounded. After the distance it asks whether to keep the original, Keep both offered: kept, the offset and the original are the outline and the hole of one sketch, whichever is outside, so a gasket or a wall is one step; Replace swaps the loop for its offset. An inward offset the shape cannot take is said in the status bar and changes nothing. |
| `Trim` | | A tool, like Line: while it is live the piece under the pointer lights up, and each click cuts the piece of line, arc, circle, ellipse or spline there back to where it next crosses another figure, or to its own end. A chain opens or comes apart there, a circle becomes the arc that is left and an ellipse the elliptical arc, and a slot is cut as its lines and caps. It stays live until another tool is chosen or Esc is pressed; a click on nothing, or on a piece that crosses nothing, says why in a box. |
| `Mirror...` | | Copy figures across a line, keeping the originals or replacing them: every figure or one, across the X or Y axis of the sketch plane or any straight segment drawn. |
| `Pattern...` | | Repeat a circle inside the outline of the sketch being drawn, as one sketch step: linear along the sketch's x or y, circular about the centre of another circle or arc or a centre typed, or a grid. Copies that would leave the outline, or overlap a hole or each other, are refused and nothing is drawn. |
| `Linetype...` | | Draw figures in a linetype: every figure or one, continuous, dashed, centre or phantom, written as `linetype=` on the figure's call in the model. It changes how the figure is drawn and exported, not what an extrude or a revolve makes of it. Also on the right-click menu while sketching. |
| `Break` | | A tool, like Trim: each click splits the line, arc or curve there in two at that place, keeping both; a closed loop or a whole ellipse opens there instead. A circle, which one cut leaves whole, is refused. |
| `Extrude...` | | Extrude the closed sketch by a height that is asked for. |
| `Revolve...` | | Revolve the closed sketch about an axis by an angle that is asked for. The axis is the sketch plane's own x axis, drawn in the view while the angle is asked. An outline with one straight side on the axis is turned into a solid with no hole; one that crosses the axis is refused, saying where: "the outline crosses the axis at (10, 0) and (0, 0)". |

A sketch click snaps to what is within a few pixels of it, trying in order:
a point already drawn, a straight segment's midpoint, an arc's or circle's
centre, the nearest place on a straight segment, the sketch plane's own axes,
and a grid whose spacing follows the zoom. A small mark at the pointer shows
the snap that would fire. Hold Alt to snap to nothing.

A point already drawn can be dragged with the left button: it snaps as a
click does, the constraints are solved again as it moves with every other
point held, and a drag they will not allow leaves it where it was. One drag
is one Undo. While a sketch is open, Delete (it reads Delete Segment) takes
away the segment under the cursor: a closed loop opens there, and an open
chain can lose either end segment. The picked parts are not touched.

### Sheet Metal

The same three are on the Sheet Metal toolbar.

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Base Flange...` | | Make the closed sketch in hand, drawn with the line tool or as one rectangle with the rectangle tool, a sheet part: the outline a sheet's thickness thick, with each circle drawn wholly inside it cut through as a hole (an outline may hold arcs, as a slot's does, and one circle alone is a disc; no flange is bent on an arc, and the flat pattern keeps the arcs) and each rectangle drawn wholly inside it with the rectangle tool cut through as a cutout (`cutouts=` is written only when there are some). One dialog asks the material and a stocked gauge of it, or Custom and the thickness, the bend radius and the K-factor, each offered as it was last given; each number is checked as it is typed, the reason beside it, the view shows the plate faintly as it would be made, and OK, enabled only when it can be, writes a `base_flange` line into the model. |
| `Flange...` | | Bend a flange on an edge of the picked sheet part. One dialog holds every choice: the edge (edge n runs from corner n to corner n + 1), from its list or by clicking it in the view, where the free edges are highlighted and the ones with a flange already are drawn grey and cannot be chosen, and after the outline's edges the list offers the edges of each flange already there, the two ends of its leg and its free edge, named as "Edge 3 leg, start end, 114 mm" and "Edge 3 return, free edge, 194 mm", each clicked in the view as the outline's are and written into the model as `(3, 'start')` or `(3, 'free')`; the length, and whether it runs to the leg or to the outside mould line (`length_from="outside"` is written only then); the angle (180 for an open hem); up or down; the flange's own bend radius (offered as the sheet's; `bend_radius=` is written only when it differs); how far in from the edge's start and end it begins and stops (0 for the full edge); whether to cut a bend relief slot beside each inset end; its return length, a second 90 degree bend at the leg's end and a return leg that long (0 for none; `return_length=` is written only when it is above 0); the holes through its leg, as one line `u, v, d; u, v, d` (u along the edge, v out from the bend, d the diameter; empty for none; `holes=` is written only when there are some); and the cutouts through its leg, as one line `u, v, w, h; u, v, w, h` (the centre's u and v as a hole's, w along the edge and h along the leg; empty for none; `cutouts=` is written only when there are some). Beside the fields a cross-section diagram shows what each means, the element of the field in focus highlighted. Each value is checked as it is typed, the reason beside its field; the view shows the flanged part faintly as it would be made; and OK is enabled only once it can be made, so nothing is refused after it. OK wraps the part's line in the model in `flange`, one undo entry. |
| `Export Flat Pattern...` | | Write the picked sheet part's flat pattern as a DXF for a laser or a plasma table: the outline on layer CUT, the bend lines on BEND and each bend's label on NOTES, its number and its note, turned along its bend line and placed so that no two labels touch and none touches the outline; the blank's rectangle and its size on BLANK; and the bend table on BEND-TABLE, a row a bend with its angle, up or down, its radius, its allowance and how far its line lies from the blank's edge chosen in Settings > View, and an ORDER column left empty to be filled in by whoever bends the part. A shop's export profile writes the flat its own way, without these. The save dialog offers DXF and SVG: a name ending .svg is written as an SVG, with the bend lines dashed, and any other as a DXF, as `dxcad flat --output` does. |
| `Show Flat Pattern` | `Ctrl+Shift+F` | Switch the view between Formed and Flat, the toggle staying pressed while Flat is shown; it is on the view's right-click menu too. Flat draws the picked sheet part as its flat alone, the other parts hidden and nothing of the formed part: the flat outline extruded by the sheet's thickness, every hole and cutout cut through it, flat on the XY plane, looked at straight down and fitted, with each bend's line and its label, turned along the line and clear of the others, the blank's rectangle drawn faintly with its size over it, and the bend table under it. Again, Formed puts the part, the other parts and the camera back as they were. It is a view, so the model, the parts and the undo history are unchanged, and the part is still counted once. Settings > View can show the formed part faintly behind the flat. |
| `Bend Table` | | On the Sheet Metal menu only, not its toolbar: show the picked sheet part's bend table in a box, one line per bend as `dxcad flat --bends` prints it, such as `bend 1: UP 90 R2, allowance 4.524 mm, length 50.000 mm`, or `No bends.` for a part with none. With no sheet part picked it is refused as Export Flat Pattern is. Changes nothing and adds no undo step. |

### Drawing

What is put on a drawing; off unless a drawing tab is in front.

| Action | Key | What it does |
|---|---|---|
| `Add View...` | | Put one more view on the drawing: Front, Top, Right, Left, Back, Bottom or Isometric, of the whole model or, where it has several parts, of one part or one sub-assembly of it. Once chosen the view follows the cursor over the sheet, and a click puts it there, at the drawing's scale, with its hidden lines and its label; `Esc` leaves it and adds nothing. A view projected from the front goes in line with the front view where the sheet has one: Top and Bottom above and below it, Right, Left and Back beside it, so only how far along that line is taken from the click; the Front and the Isometric go where they are clicked. Each add is one undo step, the file keeps it, and it is a view like any other: a click selects it, a drag moves it and Delete takes it off. Also on the sheet's right-click menu. |
| `Add Part Sheets...` | | Give parts of the drawing's model a sheet each. The model's sub-assemblies and parts are listed with a tick box each, none ticked; every ticked one gets a sheet of its own, on the drawing's sheet size and title block with the part's name, part number and material filled in, drawn alone in the sheet's four views: front, top, right and isometric. The sheets show as tabs along the bottom of the drawing, each named after its part, after the drawing's own sheet, which stays first; a click on a tab brings that sheet to the front, and every command of a drawing then works on it. They are made five at a time: after each five the window says which were made and asks whether to make the next, with `Next 5`, `Stop here`, which keeps those made, and `Cancel`, which takes every sheet of the run back. The sheets made are one undo step, and the drawing's file keeps them. |
| `Line` | | Draw a straight line on the drawing's sheet: click where it starts and where it ends. Each click snaps to the nearest drawn point of a view within reach, as an add-on's sheet tools do, and with `Ortho` on the line runs across or up the sheet; a green line follows the pointer from the first point, and `Esc` takes the first point back, or with none ends the command. The line is drawn in the drawing's line type, chosen under Line type in Drawing properties: thin, thick (printed as a view's visible edges), centre (long dash and short) or hidden (dashed). Right-click a line for its own Line Type, and for Attach to View, which makes a line drawn over a view move with the view when it is dragged or rescaled, or Detach from View, which leaves it where it is on the sheet. A click selects a line, its points show as handles to drag, and Delete takes it off. Each change is one undo step, the drawing's file keeps the lines, and the PDF and DXF exports carry them on their own layers: LINES, LINES_THICK, LINES_CENTRE and LINES_HIDDEN. |
| `Polyline` | | Draw lines through several points on the drawing's sheet: click each point, then press `Enter` to finish, with two points or more. The points snap, and follow `Ortho`, as `Line`'s do; `Esc` takes the last point back, or with none ends the command. The polyline is one line of the drawing's line type, and everything said of `Line` holds for it. |
| `Ortho` | `F8` | Turn Ortho on or off: while it is on, each new segment of a `Line` or `Polyline` runs across or up the sheet, whichever is nearer the pointer. |

### Window

How the open documents are laid out (item 681). The window opens them as the
last window left them.

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Tile` | | Show every open document at once, as inner windows side by side filling the window, each with its own 3D view of its own parts, its own minimise, maximise and close buttons, and its file name as its title. A click on one brings its document to the front, and the Parts, History and other docks follow it; its cross closes it as its tab's does, asking to save it first when it has changes; maximising it goes back to tabs. The same button, a rectangle split in two, is at the right of the tabs. |
| `Cascade` | | The open documents as inner windows, as Tile, overlapping from the top left. |
| `Tabs` | | Back to one tab per document, the one in front filling the window. The default. |

### Drafting Pro

Drafting Pro is a paid add-on (item 742). Until it is installed, its commands are listed here in italics with a padlock, each named with the add-on's name; command search finds them too. Once it is installed its own commands take their places.

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Dimensions - Drafting Pro` | | Place dimensions on a drawing's views by picking edges and points. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Balloons - Drafting Pro` | | Number the parts on a drawing with balloons that match its parts list. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Hole tables - Drafting Pro` | | List a view's holes in a table, with their positions and sizes. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Tolerances - Drafting Pro` | | Give a dimension its limits or fits. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `GD&T frames and datums - Drafting Pro` | | Add geometric tolerance frames and datum symbols. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Surface texture and weld symbols - Drafting Pro` | | Add surface texture and weld symbols to a drawing. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Revision table and notes - Drafting Pro` | | Keep a drawing's revisions in a table, and its general notes. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Automatic dimensioning and ballooning - Drafting Pro` | | Dimension and balloon a drawing's views in one step. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Section view - Drafting Pro` | | A drawing view cut along a line through the part. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Detail view - Drafting Pro` | | An enlarged view of part of another view. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Shaded view - Drafting Pro` | | A drawing view shaded as the 3D view shows the part. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |
| `Exploded view - Drafting Pro` | | A drawing view of an assembly with its parts drawn apart. Greyed: it opens a panel saying what Drafting Pro adds, its price and a Buy link, and runs nothing. |

### Fabrication

Fabrication is a paid add-on (item 742). Until it is installed, its commands are listed here in italics with a padlock, each named with the add-on's name; command search finds them too. Once it is installed its own commands take their places.

| Action | Shortcut | What it does |
| --- | --- | --- |
| `Shape library - Fabrication` | | Ready-made sheet-metal shapes, sized from a few numbers. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Cones - Fabrication` | | A sheet-metal cone or frustum, and its flat. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Transitions - Fabrication` | | Square-to-round and other transitions, and their flats. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Elbows - Fabrication` | | Segmented elbows for ducts and pipes, and their flats. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Branches - Fabrication` | | Tees and branches where two ducts meet, and their flats. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Weldments - Fabrication` | | Frames of structural members, cut and listed. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Nesting - Fabrication` | | Lay the flats out on sheets of stock with as little waste as fits. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Bend allowance tables - Fabrication` | | A shop's own bend allowances by material, thickness and tool. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |
| `Calibration wizard - Fabrication` | | Work out a press brake's K-factors from test bends. Greyed: it opens a panel saying what Fabrication adds, its price and a Buy link, and runs nothing. |

### Help

| Action | Shortcut | What it does |
| --- | --- | --- |
| `User Guide` | | Open this guide inside DX-CAD, in a help window of its own, at its first page. The pages are the ones DX-CAD was installed with, so it opens with no network. |
| `Help on This` | `F1` | Open the guide at the topic of what you are at: the dialog that is open, the command a menu has highlighted or the toolbar button under the pointer, the command being carried out, or the panel the focus is in; see [The help window](#the-help-window). With none of those it opens the first page. |
| `Licence...` | | Where this install's licence stands: free under the launch offer until 23:59 UK time on 15 November 2026 (from 30 days before, the notice "Free launch offer ends on 15 November 2026", also shown at start 30, 14 and 7 days before), or until the 30-day trial ends if that is later (it counts from this install's first start, during the offer too), then a licence. The add-ons the launch offer grants, Fabrication and Drafting Pro, stay free through that trial while no licence key is held, and lock with editing on the lock day; the line under the status names them and the day, as the notices do. Type a key (DXC-XXXXX-XXXXX-XXXXX-XXXXX) and press Activate, or sign in with your email: type the address the licence was bought with, press Send code, type the six digits from the email and press Sign in (one licence activates at once; several are listed to choose from); Deactivate gives the seat back for another computer. An activated licence works offline for up to 14 days. With no offer, trial or licence, every file still opens, shows and exports, and only editing and saving are locked. The box shows the install id the licence service counts a seat by. |
| `Add-ons...` | | List every installed plugin with its version, publisher, licence state and whether it is enabled. Install from File... takes a plugin wheel (.whl), checks it is a DX-CAD plugin for this platform and plugin API, refusing it with the reason if not, and installs it into DX-CAD's own add-ons folder; Disable keeps the plugin picked installed but not loaded, Enable loads it again, and Remove uninstalls it. Each change takes effect when DX-CAD is restarted. `dxcad addons` does the same from the command line. |
| `Licences...` | | Show THIRD-PARTY-NOTICES.md as this copy of DX-CAD ships it: every library it runs on with its version and licence, and the LGPL texts in full. |
| `Keyboard Shortcuts` | | A table of every action that has a shortcut, by menu, action and keys, read from the window's own actions, with a box to search it. The same table is under [Keyboard shortcuts](#keyboard-shortcuts) below. |
| `Search Commands...` | `Ctrl+K` | A box over every command that can be used now: each word typed narrows the list to the commands whose name holds it, or another name it commonly goes by (Base Flange/Tab, Edge Flange, Hem, Miter Flange, Flat Pattern, Flatten, Mate, SmartMates, Exploded View, Bill of Materials), and Enter or a double click runs the one picked. Those commands' tooltips say the other names too ("Also called: ..."). |
| `Open Log Folder` | | Open the folder DX-CAD's log is kept in, `DX-CAD\logs` under your local app data on Windows. The log holds the version, the platform, each action and each refusal, and any error in full, in five files of up to 1 MB; nothing in it is sent anywhere. |
| `Copy Support Report` | | Put the support report on the clipboard, the text `dxcad doctor --report` prints, for a bug report: the versions of DX-CAD, Python, OCCT and Qt, the OS, the OpenGL renderer and version, where the settings and the log are kept, the plugins and their state, the theme and the log's last 50 lines. Your own folder is written as `~`, and nothing personal is in it. |
| `Check for Updates` | | Ask GitHub for DX-CAD's latest release and say either "DX-CAD is up to date" or "Version X is available", with a link to the release. Offline, or on any error, the status bar says it could not check. Nothing is sent but the request itself. Settings > Updates > Check for updates at start, off until you switch it on, asks as the window opens and says only a newer release, in the status bar. |
| `About DX-CAD` | | Say which version of DX-CAD this is and the commit it was built from, the Python, OCCT (cadquery-ocp) and Qt it runs on, and the platform; the licence (the DX-CAD EULA, free until 15 November 2026, then a 30-day trial; the SDK under Apache 2.0), with a link to the third-party notices; the patent line and Designmatix Ltd; and links to the website, these docs and the issues. Copy puts the version lines on the clipboard for a bug report: the same lines `dxcad --version --verbose` prints. |

Every 5 minutes, and each time a model is run, every tab with changes that
are not saved is kept in a recovery folder (`DX-CAD\recovery` under your
local app data on Windows), one file per tab, gone once the tab is saved or
closed. If DX-CAD did not close cleanly, the next start lists what was kept,
by name and time, with `Recover` (each opens as a tab with its changes; Run
builds it again), `Discard` and `Later`. How often is a setting, under
Recovery in the Settings dialog; 0 switches it off.

When something goes wrong that DX-CAD did not expect, it writes the whole
story to the log and shows a box with one line saying what happened and
three buttons: `Copy Details` puts the version, the platform and the error in
full on the clipboard, for a bug report; `Open Log Folder` opens the log; and
`Continue` closes the box, and the window carries on.

## The help window

Help > User Guide opens this guide in a window of DX-CAD's own, at its first
page. `F1` opens it at the topic of what you are at, looked for in this
order: the dialog that is open; the command a menu has highlighted, or the
toolbar button under the pointer; the command being carried out (the sketch
tool that is live, a part being moved, a view being placed on a drawing,
Zoom Window waiting for its rectangle, a section view); the panel the focus
is in; and, with none of those, the first page. Every dialog of DX-CAD's own
has a `?` button beside its other buttons that opens the same topic as `F1`
does there. An add-on's dialogs are the add-on's own and have none.

In the help window, Back and Forward go through the pages looked at, Start
goes to the first page, and a link opens the page it names; a link to a web
address opens in your browser. The box at the top searches the topics, every
heading of the guide and every command by the words typed, and Enter or a
click opens the one picked. The window takes the light or the dark theme
with the view, and it stays open while a dialog is.

A command that is carried out in steps has them at the top of its topic, a
line each. Asked for while the command is under way, with `F1` or `?`, the
help says which step you are on, marked, and the steps left: a line being
drawn, a part being moved, a view being placed, a rectangle being dragged for
Zoom Window. The commands a new user meets first also have a short
animation of the command carried out on an example, shown above the page: it
plays as the topic opens and goes round until Pause is pressed, and Play
starts it again.

## The panels

What each part of the window is, which is where `F1` lands with the focus in
it.

### The 3D view

The document's parts, drawn by the OpenCASCADE viewer. A left drag orbits,
a middle drag pans and the wheel zooms at the pointer; a click picks the
part, face or edge under it, and Ctrl+click adds one to what is picked.
File > Settings > Controls can make the middle button orbit instead. The view's right-click menu has the
commands that act on what is picked. Fit, the seven views and the display
modes are under View and on the View and Display toolbars.

### The drawing sheet

A drawing tab shows its sheet in the view's place: the views, their sizes
and labels, the title block and the parts list. A click selects a view and a
drag moves it; the wheel zooms at the pointer and a middle drag pans, and
View > Fit Sheet shows the whole sheet again. A right-click on a view or on
the sheet has what can be changed there. With several sheets, the tabs along
the bottom choose the one shown.

### The Parts list

The Parts dock, on the left: the document's parts in the model's order, a
sub-assembly's parts under it. A click on a row picks the part and puts the
model pane on its line, and the eye beside a row hides or shows the part.
Under the list are the picked part's properties: its name, volume, size,
material, mass and colour. View > Parts shows or hides the dock.

### The History list

The History tab beside Parts: every edit the undo history holds, oldest
first, the current one marked. A click on an earlier entry undoes back to
it, and on a later one redoes to it. View > History shows or hides it.

### The Feature Tree

Each part in the order the model builds it and, beneath it, its features,
its sketches and its mates. A click on a row picks the part and puts the
model pane on that row's line. Nothing in the tree is dragged or
re-ordered. View > Feature Tree opens and closes it. A double click on a
flange's row, or Edit Flange... on its right-click menu, opens
[the Flange dialog](#the-flange-dialog) on that flange.

### The output pane

Under the model pane: what the last run printed, and what a command
refused and why. View > Output shows or hides it.

### The Assistant

The Assistant dock, along the bottom of the view: type a request and the
steps taken to build or change the document show in the chat, each one
written into the model and one Undo. Stop ends a turn. View > Assistant, or
`Ctrl+Shift+A`, shows or hides it, and File > Settings > Assistant chooses
the provider and its model.

### Drawing properties

While a drawing tab is in front, the left dock shows the sheet's size, its
Title Block..., the parts list's columns and, for the view clicked on the
sheet, its label, its scale and its hidden lines.

A new view's hidden lines are off: tick Hidden lines to show that view's, a
view Add View put there as much as one of the sheet's four. Leave out small
parts, with a size in mm, leaves the parts whose largest size is under it
out of that view's lines only; the other views, the view's sizes and the
parts list are as they were.

Line type is the type Drawing > Line and Polyline draw with: Thin, Thick,
Centre or Hidden. The drawing's file keeps it, and a change is one undo
step; a line already drawn keeps its own type, changed on its right-click
menu.

Text height is the height the drawing letters in: Sheet's own, 2.5, 3.5, 5
or 7 mm. The views' labels, the title block's fields, the dimensions and an
add-on's annotations take it; the drawing's file keeps it, and a change is
one undo step.

### Large assemblies on a drawing

A drawing of a model of more than 100 parts (the number is in File >
Settings, under Drawings) asks once, as it is made: "This is a large
assembly. Lay it out for speed: one view per sheet, scaled to half the sheet
and centred, the parts list on a sheet of its own, hidden lines off?" Yes
makes a sheet each for the front, top, right and isometric views and one for
the parts list, as tabs along the bottom; No makes the usual sheet. Either
way each sheet is one like any other afterwards: its scale, its view's
place, its hidden lines and what it shows are changed as on any sheet, and a
view taken off is put back with Add View.

Only the sheet on screen is worked out; another is worked out when its tab
is shown. Export Drawing writes every sheet: a page each in a PDF, side by
side in a DXF.

A large view shows at once as its outline, every edge seen straight through,
and its lines, with what is hidden taken out, come in behind while the
window stays free; the status bar says how many views are still being worked
out.

### The start page

Shown when nothing is open: New, Open, the recent files, the examples as
pictures (one click opens an example as a new unsaved tab), a link to these
docs and Connect Claude Desktop. View > Start Page brings it back.

## The dialogs

One topic for each dialog of DX-CAD's own, which is where its `?` button
and `F1` open this guide. The command that opens each is under
[The menus](#the-menus).

### The About box

Help > About DX-CAD: the version and the commit it was built from, the
Python, OCCT and Qt it runs on, the platform, the licence and the links.
Copy puts the version lines on the clipboard for a bug report; Close shuts
the box.

### The Add-ons box

Help > Add-ons...: every installed plugin with its version, publisher,
licence state and whether it is enabled. Install from File... takes a plugin
wheel, Disable and Enable switch the one picked off and on, and Remove
uninstalls it. Each change takes effect when DX-CAD is started again.

### The Bill of Materials box

Model > Bill of Materials...: the parts as lines, with how many of each,
volume, mass and size. Save CSV... writes the same table to a file; Close
shuts the box and changes nothing.

### The command search

Help > Search Commands..., or `Ctrl+K`: type part of a command's name, or
of another name it commonly goes by, and the list narrows to the commands
that can be used now. Enter or a double click runs the one picked; Esc
leaves without running anything.

### The error box

Shown when something went wrong that DX-CAD did not expect: one line saying
what happened, with the whole story in the log. Copy Details puts the
version, the platform and the error on the clipboard, Open Log Folder opens
where the log is kept, and Continue closes the box; the window carries on.

### The Flange dialog

Sheet Metal > Flange...: every choice of a flange on an edge of the picked
sheet part, the edge, the length, the angle, up or down, the bend radius,
the insets, the reliefs, the return, and the holes and cutouts through its
leg. Each value is checked as it is typed, with the reason beside its
field, the picture beside the fields shows what the field in focus means,
and the view shows the part faintly as it would be made. OK is enabled only
when the flange can be made. The Edge list holds the outline's edges and
then the edges of the flanges already there: the two ends of each one's leg
and its free edge, so a part with a flange on every edge of its base can
take more. On one of those Direction reads "towards the inside", the side
that flange's own bend has its inside, and "outward", and relief is
refused. F1 shows the command's steps, the one in hand marked. The corner
post of [the tutorial](tutorials/corner-post.md) is built with this dialog
alone. Return angle and Return turns bend a return its own way: any angle
above 0 and below 180, turned in, back over the base, or out, away from it;
they are read only when Return length is above 0. Hem makes the flange a
hem by name: closed, the leg folded flat onto the base, or teardrop, bent
past 180 round Teardrop radius until its free edge comes down to the base.
While one is chosen Angle and Bend radius are grey, since a hem has its own,
and Teardrop radius is read for a teardrop alone; an open hem is still
Angle 180 with Hem left at none.

All edges puts a flange on every free edge of the outline in one go. Ticked,
a table opens under the fields with a row for each of those edges: the edge,
then its Length, Length to, Angle, Direction, Bend radius, Return length,
Start inset, End inset and Corners. Every row starts with the fields' values
as they stood and is then its own; a number is typed in its cell and a choice
made in its list. A row whose edge is unticked gets no flange. The flanges
are made in the rows' order and are one undo step. A table's flanges take no
relief, holes or cutouts: those are given to one flange, with the box
unticked.

When a value is wrong the dialog says which edge, which value and why, as
"Edge 2: Angle 200: an angle is above 0 and at most 180." When each value is
right in itself but the flange would run into the part, it names the length
to shorten, the return first and then the leg, and the longest that works
there, which it finds by making the flange shorter.

Edit Flange changes a flange the model already has. Double-click the
flange's row in the Feature tree, or right-click it and choose Edit
Flange...: the dialog opens with the values the flange was written with, its
edge kept. OK writes the flange() call again and builds the part from that
flange on, everything made after it included, as one undo step. The view
shows nothing of the edit until then. A flange whose values the model works
out, from a variable or a loop, is changed in the model pane, which is put
on its line; an edit after which a later step no longer builds is refused
with that step's reason, and nothing changes.

### The Base Flange dialog

Sheet Metal > Base Flange...: the material and a stocked gauge of it, or
Custom with the thickness, the bend radius and the K-factor, for the sheet
part made from the closed sketch in hand. Each number is checked as it is
typed, and OK is enabled only when the part can be made.

### The Check Interference box

Model > Check Interference...: the pairs of parts that overlap, each with
the volume they share. The overlaps show in red in the view until the box
is closed.

### The Licences box

Help > Licences...: the third-party notices as this copy of DX-CAD ships
them, every library it runs on with its version and licence, and the LGPL
texts in full.

### The Licence box

Help > Licence...: where this install's licence stands. Type a licence key
and press Activate, or sign in with the email address the licence was
bought with: Send code, then the six digits from the email and Sign in.
Deactivate gives the seat back for another computer. The box shows the
install id a seat is counted by.

### An add-on's panel

A greyed command of an add-on that is not installed opens a short panel:
the command, the add-on it belongs to and what the add-on adds, with a Buy
button that opens the add-on's page in your browser. Nothing is run and
nothing is sent.

### The Add Part Sheets box

Drawing > Add Part Sheets...: the model's sub-assemblies and parts, each
with a tick box, none ticked. Tick the ones that are to have a sheet of
their own and press Make Sheets; Cancel adds nothing. The sheets are
made five at a time, with a question after each five.

### The recovery box

Shown at the start when DX-CAD did not close cleanly: the tabs that had
changes not saved, each by its name and when it was kept. Recover opens
every one as a tab with its changes, Discard throws them away, and Later
leaves them for the next start.

### The Settings dialog

File > Settings...: the settings in groups. Mode is 2D drafting or 3D
modelling; View holds Show Planes; Recovery, the minutes between keeps of
the unsaved tabs; Parts, the default material; Updates, whether to check at
the start; Controls, DX-CAD's own mouse and keys or the classic CAD
controls; and Assistant, its provider, model and address. OK keeps the
changes and Cancel leaves everything as it was.

### The Keyboard Shortcuts box

Help > Keyboard Shortcuts: every action that has a shortcut, by menu,
action and keys, read from the window's own actions. The box at the top
searches actions and keys.

### The Suggest Mates box

Model > Suggest Mates...: the mates the picked part's features allow
against the parts near it, best first. Picking a row shows where the part
would go. Tick the ones to add and press Accept Checked, or Accept All;
Cancel adds none.

### The Title Block dialog

File > Title Block...: the fields filled in once for every drawing,
company, drawn by, checked by, material, finish, general tolerance, drawing
number and revision, and the font and height the drawing is lettered in. OK
keeps them for every drawing made after; Cancel leaves them as they were.

### The What's New box

Shown once after an update: what changed in the version now installed, as
its release notes say it. Close shuts it.

## Keyboard shortcuts

Every action that has a shortcut, as Help > Keyboard Shortcuts lists it.
The table is written by `python -m dxcad.docsgen shortcuts` from the
window's own actions, and a test fails if it drifts. Ctrl is Cmd on a Mac.

<!-- generated by python -m dxcad.docsgen shortcuts -->

| Menu | Action | Keys |
| --- | --- | --- |
| File | New Part | `Ctrl+N` |
| File | Open... | `Ctrl+O` |
| File | Save | `Ctrl+S` |
| File | Save As... | `Ctrl+Shift+S` |
| File | Save Model | `Ctrl+Shift+M` |
| Edit | Undo | `Ctrl+Z` |
| Edit | Redo | `Ctrl+Y` |
| Edit | Delete | `Del` |
| View | Zoom Window | `W` |
| View | Hide | `H` |
| View | Show All | `Shift+H` |
| View | Continuous Orbit | `Ctrl+Shift+O` |
| View | Assistant | `Ctrl+Shift+A` |
| Model | Run Script | `F5` |
| Sheet Metal | Show Flat Pattern | `Ctrl+Shift+F` |
| Drawing | Ortho | `F8` |
| Help | Help on This | `F1` |
| Help | Search Commands... | `Ctrl+K` |
| Window | Next Tab | `Ctrl+Tab` |
| Window | Previous Tab | `Ctrl+Shift+Tab` |

<!-- end of generated shortcuts -->

## The model pane

The pane on the right is the model.py, and it is the document's source of
truth: the shapes in the scene are what the last run of that text built.
Typing in it changes nothing until the model is run.

- **Run Script**, or **F5**, runs it. What it prints goes to the output pane,
  and a model that raises puts the cursor on the line that raised, with the
  helper file's own line above it when the failure was in a file beside the
  model.
- **Run on Change** watches the model.py on disk, and its helpers, and runs
  the model again whenever one of them is saved. It is for an editor in
  another window: the pane follows the file rather than the other way round.
  It is off for every new window and is taken off again by New and by Open.
- **No Time Limit** lifts the minute a run is given. A run happens on the
  window's own thread, so a model that never ends is a window that never
  answers again; the limit is there so that a typo costs a minute rather than
  everything typed since the last save.
- **Check Model** runs the model and says what it would change without
  changing anything, and **Show in Script** goes the other way, from a part in
  the scene to the line that built it.
- **Adopt Parts** is for a document holding parts no model builds, which is
  what an older project looks like: it writes each of them to a file beside
  the project and adds the line that reads it back, so the model builds
  everything again.

## The model a project carries

A part or assembly file is something people are sent, and the model inside one is a program.
So a project opened from a file is asked about before its model is run for the
first time, by Run, by F5 or by Run on Change: the question says that a model
is Python and runs with your own permissions, and names the project. Answering
no runs nothing and changes nothing. Answering yes runs it, and the window
does not ask again until it is given another project.

A model you opened by name, one you typed into a new project and one the
window wrote itself are your own and are never asked about.

Whether any of this looks right on a desktop is a manual check: the suite
drives the window offscreen, where nothing is drawn. The scene itself, the
orbiting and the picking, is the one part of DX-CAD no test can see.
