# Drawings and model.py

A drawing, a `.dxcdrg` file, is a sheet drawn from a part or assembly file:
its standard views, dimensions, hole callouts and parts list, the views and
annotations of any plugin, and a title block. The window opens one in a tab of
its own, and `dxcad drawing FILE.dxcdrg --output sheet.pdf` writes it as a
PDF or a DXF. Every time a drawing is drawn it is drawn from its model as the
model is now, so a drawing follows every change to the part.

A drawing of an assembly may hold a sheet for each of its parts as well:
Drawing > Add Part Sheets... lists the parts and sub-assemblies with a tick
box each, and every one ticked gets a sheet of its own, drawn alone in the
sheet's four views, its name, part number and material in the title block.
The sheets are tabs along the bottom of the drawing and are kept in its
file, under `"sheets"`; `dxcad drawing` and Export Drawing write one sheet,
the drawing's own from the command line and the one in front from the
window.

This page is for a plugin that extends drawings, and for a model that uses
what such a plugin adds.

## Drawing functions

A plugin may add functions to the model language that work on a drawing:

```python
def label(drawing, part, words):
    """Put a note with `words` on `part` in the front view."""
    notes = drawing.annotations("myplugin")
    notes.append(
        {"kind": "myplugin.note", "view": "front", "ref": {"part": part},
         "data": {"text": words}}
    )
    drawing.set_annotations("myplugin", notes)


def register(registry):
    registry.drawing_function("label", label)
```

A model.py then calls `label("plate", "DEBURR ALL EDGES")` after the parts, as
it calls any other name of the model language. When the model is run for its
parts, by Run Script, `dxcad run` or the agent door, the call does nothing.
When a drawing of the model is drawn, on screen or for an export, the model is
run once more for the drawing, and each drawing function it called is called
with the drawing being drawn, `label(drawing, "plate", "DEBURR ALL EDGES")`,
in the order the model called them. What they add is drawn on the sheet each
time the drawing is drawn; it is the model's, so the drawing file itself is
not changed by it.

A model that fails when it is run for the drawing, and a drawing function that
raises, are said among the sheet's warnings, on the window's status bar and on
`dxcad drawing`'s stderr; the rest of the sheet is drawn as usual.

## The drawing a plugin is handed

A drawing function, and a plugin's MCP tool registered with `drawing=True`,
are handed the drawing as an object with three calls:

| Call | What it does |
| --- | --- |
| `drawing.annotations(plugin)` | The plugin's annotation records on the drawing, each `{"kind", "view", "ref", "data"}`, as copies. |
| `drawing.set_annotations(plugin, records)` | Puts `records` in place of the plugin's annotations. In the window this is one undo step. |
| `drawing.scale(view)` | A view's scale as drawn over true, 0.5 for 1 : 2: a standard view by name (`"front"`, `"top"`, `"right"`, `"iso"`), or a plugin's view as `(plugin, index)`. None for a view the drawing has not got. |

A tool registered with `registry.tool(..., drawing=True)` is called as
`call(document, arguments, drawing)`. Called from the window, over
`dxcad serve --window`, it is handed the drawing tab in front, and what it
changes is one undo step with the rest of the call. It may also be called with
a `"drawing"` argument naming a `.dxcdrg` file, from the server's directory
like every path a tool is given; it is then handed that file, and
`set_annotations` writes the file again. With neither, the call is answered
with an error saying so. The argument is added to the tool's schema for it.

DX-CAD adds no tool or function of its own that suggests dimensions or
balloons: it hands plugins the drawing, and what they place there is theirs.

## Where the user adds a view

So a message can name the place (item 862): a standard view is added with
**Drawing > Add View...**, or **right-click on the sheet > Add View...**; a new
drawing's first four views come with **File > New Drawing**; and a plugin's
view, such as a detail or a section, with its sheet tool on the
**right-click menu of the sheet** and on the **plugin's own menu**, the menu
bar's menu named after the plugin. [Plugins](plugins.md) says each in full.
