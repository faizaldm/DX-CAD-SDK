# Help: animations still to make

The help window shows a command's steps at the top of its topic, and with
them a short animation of the command carried out, where one has been made
(item 817). A command with steps and no animation yet shows its steps as
text, and is listed here, the commands a new user meets first at the top.

An animation is made by a scene in `dxcad.gui.help_animations` that drives
the real window, and `python -m dxcad.docsgen animations` makes every one
again; none is edited by hand. This page is written by
`python -m dxcad.docsgen help-todo`, and a test fails if it drifts.

## Still to make

| Command | Topic | Steps |
| --- | --- | --- |
| Undo | `action.undo` | 2 |
| Line | `action.tool_line` | 3 |
| Run Script | `action.run_script` | 3 |
| Flange... | `action.sheet_flange` | 4 |
| Rectangle | `action.tool_rectangle` | 2 |
| Circle | `action.tool_circle` | 2 |
| Arc | `action.tool_arc` | 3 |
| Centre Arc | `action.tool_centre_arc` | 3 |
| Polygon | `action.tool_polygon` | 2 |
| Slot | `action.tool_slot` | 3 |
| Ellipse | `action.tool_ellipse` | 3 |
| Spline | `action.tool_spline` | 2 |
| Trim | `action.trim_sketch` | 3 |
| Break | `action.break_sketch` | 3 |
| Zoom Window | `action.zoom_window` | 2 |
| Measure | `action.measure` | 4 |
| Line | `action.drawing_line` | 3 |
| Polyline | `action.drawing_polyline` | 4 |
| Section View | `action.section_view` | 3 |
| The drawing sheet | `panel.sheet` | 3 |

## Made

| Command | Topic | Animation |
| --- | --- | --- |
| Open... | `action.open` | `open.gif` |
| The 3D view | `panel.view` | `pick.gif` |
| Hide | `action.hide_parts` | `hide.gif` |
| Rename... | `action.rename` | `rename.gif` |
| Move... | `action.move` | `move.gif` |
| Add View... | `action.add_view` | `add_view.gif` |
| Add Part Sheets... | `action.add_part_sheets` | `part_sheets.gif` |
| Drawing properties | `panel.drawing_properties` | `columns.gif` |
