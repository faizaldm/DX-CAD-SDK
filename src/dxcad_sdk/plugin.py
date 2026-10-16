# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""The plugin API: what DX-CAD hands a plugin, and what a plugin hands back.

These are interfaces only. DX-CAD's own Registry, document and window meet
them; nothing here is DX-CAD, and nothing here imports it. A plugin is a
distribution that declares an entry point in ENTRY_POINT_GROUP naming a
function that takes a Registry:

    [project.entry-points."dxcad.plugins"]
    washer = "dxcad_washer:register"

    def register(registry: Registry) -> None:
        registry.require(1)
        registry.add_name("washer", washer)

What a plugin registers reaches four places: the model language (a name every
model.py starts with), the command line (a subcommand), the agent door (an MCP
tool) and the window (actions and dialogs, on a toolbar and a menu named after
the plugin). A kind of sheet part unfolds through DX-CAD's own flat pipeline;
a plugin keeps its own data in a section of the saved file; and a plugin may
say it needs an entitlement, held by a provider in ENTITLEMENT_GROUP.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator, Sequence
from typing import Any, Protocol, runtime_checkable

#: The entry-point group a plugin declares itself in.
ENTRY_POINT_GROUP = "dxcad.plugins"

#: The entry-point group an entitlement provider declares itself in: a
#: callable, or an object with `holds`, answering whether the entitlement it is
#: given by name is held.
ENTITLEMENT_GROUP = "dxcad.entitlements"

#: The version of the plugin API this SDK describes; a plugin that needs it
#: says so with Registry.require(API_VERSION).
API_VERSION = 1

#: What a locked plugin's actions, tools and files say.
LOCKED = "Requires {name}: see {link}"

#: The scopes a setting is declared with (DX-CAD item 826): the document's, kept
#: in its file and at its default in a new one; the session's, until DX-CAD
#: closes; the user's, kept across starts.
SCOPES = ("document", "session", "preference")

#: What a part made with a plugin that is not installed is marked with.
MADE_WITHOUT = "made with {plugin}, not installed"

#: What a plugin may take from DX-CAD's dxcad.plugins module (DX-CAD item
#: 759): its public names, functions a plugin calls among them. `dxcad-sdk
#: check` fails a plugin that takes any other name from it. free_area(document,
#: sheet_name) answers the rectangles (left, bottom, right, top), in mm, that a
#: draw on sheet `sheet_name`, such as "A3", would be handed as `free`, without
#: drawing the sheet: `document` is a model's Document or a DrawingDocument.
#: Item 760: gauges (SHEET_METALS with each metal's density, and the gauge
#: tables), run_model(project) answering a project's parts again or raising
#: ScriptError, load_project(path) answering its Document or raising
#: ProjectError, and export_drawing(path, out) writing a drawing to PDF or DXF
#: with no window, in place of dxcad.gauges, dxcad.script, dxcad.project and
#: dxcad.cli, which `dxcad-sdk check` warns of.
PLUGIN_FUNCTIONS = (
    "Action",
    "AnnotationKind",
    "ApiVersionError",
    "Check",
    "Command",
    "DrawingFunction",
    # DX-CAD item 797: the form a long dialog is built on, a QDialog whose
    # fields scroll while its OK and Cancel stay; see FormDialog below.
    "FormDialog",
    "Plugin",
    "PluginLocked",
    "ProjectError",
    "Registry",
    "ScriptError",
    "Setting",
    "SheetKind",
    "SheetTool",
    "Tool",
    "Unfolds",
    "ViewKind",
    "actions",
    "annotation_kinds",
    "checks",
    "collecting",
    "commands",
    "drawing_functions",
    "drawing_ready_calls",
    "drop_unheld_parts",
    "export_drawing",
    "free_area",
    "gauges",
    "held",
    "installed_names",
    "load",
    "load_project",
    "lock_of",
    "locked_tools",
    "made_without",
    "maker",
    "missing",
    "model_names",
    # DX-CAD item 815: open_window() answers DX-CAD's main window, shown, for
    # a plugin's tests to click and drag on; see open_window below.
    "open_window",
    "record_parts",
    "run_model",
    "section",
    # DX-CAD item 826: every setting the loaded plugins declared, by
    # "PLUGIN.NAME"; see Registry.setting and Setting below.
    "settings",
    "sheet_kinds",
    "sheet_tools",
    "summary",
    "tools",
    # DX-CAD item 828: the plugin that says it unfolds the parts named, and
    # its command for it; see Registry.unfolds below.
    "unfolder_of",
    "view_kinds",
    # DX-CAD item 763: view_point(view, point) answers where model point
    # (x, y, z) lies in a standard view's own plane, (u, v) in the model's mm,
    # for "front", "top", "right" and "iso": the frame a Pick's `plane` is in.
    "view_point",
)

#: dxcad.model's own calls beside the model language, which a plugin asks for
#: by name and `dxcad-sdk check` names (DX-CAD item 762): write_flat(flat,
#: path) writes a FlatPattern (outline, openings, cuts, bends, notes) to a
#: .dxf or a .svg with the layers, units and notes `dxcad flat` writes, and
#: answers the path; a nested sheet is one FlatPattern of openings and notes.
MODEL_CALLS = ("write_flat",)

#: The core's own modules a plugin imported before DX-CAD item 760, and what
#: the plugin API gives in their place: `dxcad-sdk check` warns of each.
PRIVATE_MODULES = {
    "dxcad.gauges": "dxcad.plugins.gauges",
    "dxcad.script": "dxcad.plugins.run_model and dxcad.plugins.ScriptError",
    "dxcad.project": "dxcad.plugins.load_project and dxcad.plugins.ProjectError",
    "dxcad.cli": "dxcad.plugins.export_drawing",
}

#: A JSON schema, as an MCP tool's input_schema takes it.
Schema = dict[str, Any]

#: A dialog's field: (name, label, default), the default a number or text.
Field = tuple[str, str, object]


class PartIdentity(Protocol):
    """What a shop's systems know a part by: part() takes the three by these names."""

    part_number: str | None
    revision: str | None
    #: (name, value) pairs, in the order they were given.
    properties: tuple[tuple[str, str], ...]


@runtime_checkable
class Document(Protocol):
    """The open document a tool is called with: named solid parts, in order."""

    #: Each plugin's own section of the saved file, by plugin name, each
    #: {"version": ..., "parts": [...], "data": {...}}; DX-CAD stores and
    #: returns it untouched.
    plugin_sections: dict[str, dict]
    #: The identities of parts made with no model to write them into (an
    #: agent's, say), by name; a tool that makes a part may set one here.
    identities: dict[str, PartIdentity]

    @property
    def revision(self) -> int:
        """A number that says when the document changed (DX-CAD item 839): a new,
        larger one after every change to the parts or to the model's text, and
        the same one while they stand. No two documents share one, so what was
        worked out from the parts can be kept by it and found again."""
        ...

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        """Each part as (name, shape), in document order."""
        ...

    def __len__(self) -> int: ...

    def parts_list(self) -> list[tuple[int, list[str]]]:
        """The parts list as the drawing numbers it, [(item, [part names])], the same
        numbering as the parts list on the sheet and the bill of materials."""
        ...

    def hole_groups(self, part: str, view: str) -> list[list[tuple[float, float]]]:
        """Part `part`'s groups of identical holes that `view` ("front", "top",
        "right"...) looks into, each a list of hole centres in the view's plane, in
        mm, in the order the drawing's grouped hole callouts use."""
        ...

    def view_lines(self, view: str, parts: bool | str = False) -> tuple | None:
        """Standard view `view`'s visible edges as DX-CAD draws them ("front",
        "top", "right" or "iso"), each its points (u, v) in the view's plane, in mm
        at 1:1, the frame hole_groups' centres are in. Read only, and the same
        object at every call until `revision` changes, so a tool need not project
        the model again. None while the window is still working the view's lines
        out behind it; KeyError for a view there is not (DX-CAD item 842).

        With `parts=True` each line comes with the part it is an edge or an
        outline of, `((part, points), ...)`: the same lines in the same order,
        `part` the part's name as the document names it, so which part a
        region of the view shows is read off its lines and no ray is cast
        (DX-CAD item 853). A DX-CAD from before it raises TypeError for the
        keyword.

        With `parts="all"` each line comes with every part it lies on,
        `((parts, points), ...)`, `parts` a tuple of names, the part it is an
        edge or an outline of first, then each part whose edge or outline is
        drawn under it in the view and each part whose face its edge lies on in
        space (DX-CAD item 858)."""
        ...

    def view_regions(self, view: str) -> tuple | None:
        """Standard view `view`'s visible regions, cut by its visible lines, each with
        the part seen in it, `((part, at, loops), ...)`: `part` the part's name,
        `at` a point (u, v) well inside the region where a ray from the viewer
        meets that part first, and `loops` the region's outline then the
        outlines of its holes, each its points (u, v) in order, in view_lines'
        frame. The part is the one an exact ray at `at` meets first, of two met
        at one place the one the document names first; a region where nothing
        is seen is left out. Worked out the first time it is asked for, then
        read only and the same object until `revision` changes; None while the
        view's lines are still being worked out; KeyError for a view there is
        not (DX-CAD item 866). A DX-CAD from before it has no view_regions:
        call it when hasattr(document, "view_regions")."""
        ...

    def flat_pattern(self, name: str) -> FlatPattern | None:
        """Sheet part `name`'s flat pattern, or the one flat part `name` was made
        from by flat_solid, or None for a part that is neither."""
        ...

    def colour(self, name: str) -> tuple[int, int, int] | None:
        """Part `name`'s colour as the window shows it, (r, g, b) from 0 to 255, or None."""
        ...


@runtime_checkable
class Window(Protocol):
    """The window an action is run with, inside one undo step."""

    def free_name(self, base: str) -> str:
        """A part name starting `base` that no part has yet."""
        ...

    def add_part(self, name: str, shape: Any, statement: str) -> str | None:
        """Add part `name`, and write `statement` into the model pane, as one undo entry.

        A shape that is empty or not a valid solid is not added and nothing is
        written: the reason is answered, as check_shape gives it (DX-CAD item
        796); None when the part was added.
        """
        ...

    def check_shape(self, shape: Any) -> str | None:
        """Why `shape` cannot be a part, empty or not a valid solid, or None when it
        can: what a dialog asks before it enables OK (DX-CAD item 796)."""
        ...

    def selected_parts(self) -> list[str]:
        """The selected parts' names in the order they were picked (DX-CAD item 761)."""
        ...

    def replace_part(self, name: str, shape: Any, statement: str) -> str | None:
        """Put `shape` in place of part `name`'s solid and `statement` in place of the
        model's statement that builds it, as one undo entry (DX-CAD item 761); a shape
        check_shape refuses changes nothing and its reason is answered (item 796)."""
        ...

    def part_identity(self, name: str) -> PartIdentity:
        """Part `name`'s part number, revision and properties; empty where it has none."""
        ...

    def set_part_identity(
        self,
        name: str,
        part_number: str | None,
        revision: str | None,
        properties: dict[str, str] | None,
    ) -> bool:
        """Write part `name`'s identity as its own identity() statement, as one undo entry;
        True if it took. Works however the part was made, in a loop or a helper too.

        None, or no properties, takes one out.
        """
        ...

    # The drawing tab in front: with none, reading answers empty or None, and
    # setting changes nothing, says so on the status bar and answers False.

    def drawing_annotations(self, plugin: str) -> list[dict]:
        """Plugin `plugin`'s annotation records on the drawing tab in front."""
        ...

    def add_drawing_annotation(
        self, kind: str, view: str | int, ref: dict, data: dict | None = None
    ) -> bool:
        """Put an annotation of `kind`, "PLUGIN.NAME", on view `view` (a standard
        view the drawing shows, "front", "top", "right" or "iso", or the index of
        one of the plugin's views on it), attached by `ref`, as one undo step;
        refused, with the reason on the status bar, when the drawing has no such
        view (DX-CAD item 719; the isometric view by name since item 763)."""
        ...

    def add_drawing_annotations(self, records: list[dict], label: str | None = None) -> bool:
        """Put several annotations on the drawing in front as one undo step, the
        sheet drawn once: each of `records` is {"kind": "PLUGIN.NAME", "view":
        ..., "ref": {...}, "data": {...}}, as add_drawing_annotation takes them
        one at a time, of any kinds. All or none: one naming a view the drawing
        has not got, and nothing is added. `label` names the undo step, "Add 51
        Balloons" when not given (DX-CAD item 819)."""
        ...

    def plugin_setting(self, plugin: str, name: str) -> Any:
        """What plugin `plugin`'s setting `name` is, its default until it is set:
        read where the scope it was declared with says, the document in front,
        this window until DX-CAD closes, or the user's settings. KeyError for a
        setting the plugin never declared (DX-CAD item 826)."""
        ...

    def set_plugin_setting(self, plugin: str, name: str, value: Any) -> None:
        """Set plugin `plugin`'s setting `name`, kept where its scope says: a
        document's goes into the file at the next save. `value` is plain data,
        what JSON can carry; anything else is ValueError (DX-CAD item 826)."""
        ...

    def say_doing(self, words: str) -> None:
        """Say what the command under way is doing, such as "Placing balloons...":
        when the window has been busy for a second DX-CAD shows "Please wait"
        with these words over it, where it would show the command's own name.
        They are forgotten when the command ends (DX-CAD item 820)."""
        ...

    def open_dialog(self, key: str) -> Any:
        """Show the dialog DX-CAD builds for the plugin's `registry.dialog(key, ...)`
        and answer the QDialog without waiting on it; accepting or closing it calls
        nothing. For a plugin's tests of how its fields fit and read; KeyError for
        a key no plugin's dialog has (DX-CAD item 763)."""
        ...

    def set_theme(self, name: str) -> None:
        """Put the window in theme `name`, "light" or "dark", and keep it; ValueError
        for a theme there is not (DX-CAD items 620 and 763)."""
        ...

    def set_drawing_annotations(
        self, plugin: str, records: list[dict], label: str | None = None
    ) -> bool:
        """Put `records` in place of the plugin's annotations, as one undo step. True
        too when they are the drawing's already, with nothing changed and no undo
        step; False for no drawing tab in front, or a window locked against editing
        (DX-CAD item 804). `label` names the step, so that Edit reads "Undo Balloon
        View" for label="Balloon View"; with none it is "Change PLUGIN annotations"
        (DX-CAD item 840)."""
        ...

    def selected_annotation(self) -> dict | None:
        """The record of the plugin annotation the user clicked on the sheet, or None."""
        ...

    def delete_annotation(self) -> bool:
        """Take the selected annotation's record off its plugin's list, as one undo
        step, as Delete does: only one of a kind that registers `handles`. False
        for none selected, a kind with none, or a window locked against editing
        (DX-CAD item 815)."""
        ...

    def edit_annotation(self) -> bool:
        """Call the selected annotation's kind's `edit(window, record)`, as a
        double-click on it does. True if the kind has an edit and it was called;
        what it raises is said on the status bar (DX-CAD item 815)."""
        ...

    def drawing_views(self, plugin: str) -> list[dict]:
        """Plugin `plugin`'s views on the drawing tab in front, {"kind", "at", "data"}."""
        ...

    def set_drawing_view(
        self, plugin: str, index: int, data: dict, label: str | None = None
    ) -> bool:
        """New data for the plugin's view `index`, as one undo step. True too when the
        view has that data already, with nothing changed and no undo step; False for
        no drawing tab in front, a view the plugin has not got, or a window locked
        against editing (DX-CAD item 804). The step is called `label` when one is
        given, "Undo Detail Scale" in Edit, and "Change KIND" when not (DX-CAD
        item 861)."""
        ...

    def selected_view(self) -> tuple[str, int] | None:
        """The plugin view the user clicked on the sheet, (plugin, index), or None."""
        ...

    def drawing_view_scale(self, view: str | tuple[str, int]) -> float | None:
        """A view's scale as drawn over true: a standard view by name, or a plugin
        view as (plugin, index); None for no such view."""
        ...

    def export_drawing(self, sheet: Any, path: Any) -> Any:
        """Write drawing `sheet`, a .dxcdrg file or a DrawingDocument, to `path`, PDF or
        DXF, as `dxcad drawing` does, with no drawing tab; the path written, or None
        (DX-CAD item 722)."""
        ...

    def drawing_sheet_name(self) -> str | None:
        """The size of the sheet the drawing in front is drawn on, such as "A3", or
        None when no drawing tab is in front (DX-CAD item 720)."""
        ...

    def drawing_document(self) -> Document | None:
        """The Document the drawing tab in front is drawn from, the one its
        annotations' draw is handed, or None when no drawing tab is in front
        (DX-CAD item 716). It is the same Document, holding the same shape
        objects, from call to call until the model changes, and its `revision`
        is a new number when it has (DX-CAD item 839)."""
        ...

    # DX-CAD item 784: the drawing in front as it is drawn, with its own scale,
    # view scales and moved views, where free_area(window.drawing_document(),
    # ...) lays the model out with a drawing's defaults.

    def drawing_free_area(self) -> list[tuple[float, float, float, float]] | None:
        """The rectangles a draw on the drawing in front is handed as `free`,
        (left, bottom, right, top) in mm, largest first: clear of the title
        block, the parts list and the standard views where this drawing puts
        them, at its scale and the views' own. None with no drawing tab in front."""
        ...

    def drawing_view_origin(
        self, view: str | tuple[str, int]
    ) -> tuple[tuple[float, float], float] | None:
        """Where the model's origin is drawn in view `view` of the drawing in front
        and the view's scale as drawn over true, ((x, y), scale), as a Pick
        carries them: a plane point (u, v) is drawn at origin + scale * (u, v).
        `view` is a standard view by name ("front", "top", "right", "iso") or a
        plugin's view as (plugin, index), whose origin is where it is placed.
        None for a view the drawing has not got, or with no drawing tab in front."""
        ...

    def drawing_settings(self) -> dict | None:
        """The drawing in front's own settings, a copy: "sheet", "scale" as drawn
        ((drawn, true)), "fitted", "views" (each moved view's offset),
        "view_scales", "dimensions", "parts_list", "hidden_off", "font",
        "text_height", "labels", "columns", "fields" and "precision", the
        dimensions' precision in mm (1, 0.1 or 0.01), the drawing's own or the
        one the sheet draws at. None with no drawing tab in front."""
        ...


def open_window() -> Window:
    """dxcad.plugins.open_window(): DX-CAD's main window, shown, for a plugin's tests.

    The window an action is handed, with the plugins loaded, not waiting on
    an event loop: a test opens a drawing in it (`window.open_drawing(path)`),
    sends its sheet the mouse and the keys, lets Qt handle the events and
    closes it, which asks no question. Offscreen under
    QT_QPA_PLATFORM=offscreen. Its settings, recovery files, log and channel
    are its own, in a temporary folder, unless DXCAD_SETTINGS,
    DXCAD_RECOVERY_DIR, DXCAD_LOG_DIR or DXCAD_CHANNEL is set already, so it
    never touches the user's (DX-CAD item 815). Described here; the call is
    DX-CAD's own.
    """
    raise NotImplementedError("open_window is dxcad.plugins.open_window, in DX-CAD itself")


#: What a plugin may read off the window its action is handed (DX-CAD item 761):
#: Window's calls, and the document and the two drawing tabs' openers the
#: plugins page describes. `dxcad-sdk check` names the ones a plugin uses.
WINDOW_CALLS = tuple(
    sorted(
        [name for name in vars(Window) if not name.startswith("_")]
        + ["document", "new_drawing", "open_drawing"]
    )
)


class FormDialog(Protocol):
    """The form a plugin builds a long dialog of its own on (DX-CAD item 797).

    `from dxcad.plugins import FormDialog` is a QDialog: FormDialog(title,
    parent, buttons=...) with OK and Cancel unless `buttons`, a
    QDialogButtonBox.StandardButton, says otherwise. Its fields are in a
    scroll area and its buttons under it, so the dialog is never taller than
    its screen's available height and OK and Cancel are always in reach;
    only the height scrolls. Enter accepts and Esc cancels. Subclass it, or
    make one and fill it.
    """

    #: The scrolled column, a QVBoxLayout: add_group and add_field fill it,
    #: and a dialog may add widgets and layouts of its own.
    body: Any
    #: A QVBoxLayout between the fields and the buttons, never scrolled: the
    #: place for a line saying what is wrong.
    footer: Any
    #: The QDialogButtonBox, wired to accept and reject.
    buttons: Any
    #: The QScrollArea the fields are in.
    scroll: Any
    #: Each named field's widget.
    fields: dict[str, Any]

    def add_group(self, title: str) -> Any:
        """A titled group of fields at the end of the scrolled column: its
        QFormLayout, for add_field's `group` or to fill directly."""
        ...

    def add_field(
        self, label: str, widget: Any, group: Any = None, name: str | None = None
    ) -> Any:
        """Add `widget` under `label` to `group`, or below what is there with none;
        with `name` it is kept in `fields` under it. Answers the widget."""
        ...

    def set_picture(self, picture: Any, stretch: int = 0, fields: int = 1) -> Any:
        """Put `picture`, a QPixmap or a widget, in a column beside the fields,
        where it stays as they scroll, sharing the width as `stretch` to `fields`."""
        ...

    def reveal(self, widget: Any) -> None:
        """Scroll the fields so all of `widget` is in view."""
        ...

    def in_view(self, widget: Any) -> bool:
        """Whether all of `widget`, one of the scrolled column's, is in view now."""
        ...


class SheetPart(Protocol):
    """What a kind of sheet part's builder answers: a solid and what it was built from."""

    solid: Any
    spec: Any
    #: "PLUGIN.NAME" for a plugin's kind.
    kind: str | None
    #: Whatever the builder kept for its unfolder to read.
    record: object


class Bend(Protocol):
    """One bend on a flat: its two bend lines, its angle, its direction and radius."""

    lines: tuple[tuple[tuple[float, float], tuple[float, float]], ...]
    angle: float
    direction: str
    radius: float


class FlatPattern(Protocol):
    """What an unfolder answers: the cut outline and the bends, on the base's plane.

    Build one from dxcad.model's FlatPattern, Bend and SheetSpec, which are
    the core's own classes, so flat_solid and the flat writers take it.
    """

    outline: tuple[tuple[float, float], ...]
    bends: tuple[Bend, ...]
    spec: Any
    holes: tuple[tuple[float, float, float], ...]
    cutouts: tuple[tuple[float, float, float, float], ...]
    #: Optional: cutouts through the flanges, each its four corners on the
    #: flat; the flat writers take a pattern without it as having none.
    leg_cutouts: tuple[tuple[tuple[float, float], ...], ...]
    #: Optional: the plugin's own notes, (x, y, text) in the flat's mm, written
    #: as text on the NOTES layer at those points, as the bend notes are; a
    #: fourth item, (x, y, text, height), is the note's own text height in mm
    #: (DX-CAD item 717), the bend notes' 2.5 mm otherwise.
    notes: tuple[tuple[float, float, str] | tuple[float, float, str, float], ...]
    #: Optional: open cut lines, each a polyline on the flat left open, such as
    #: the line two nested pieces share; cut and counted in the cut length,
    #: left out of the area and the solid.
    cuts: tuple[tuple[tuple[float, float], ...], ...]
    #: Optional: openings of any shape inside the outline, each a closed
    #: polygon on the flat, its first point not repeated; cut on the CUT layer,
    #: counted in the cut length and taken off the area and the mass. One
    #: outside the outline or crossing it is refused with the reason.
    openings: tuple[tuple[tuple[float, float], ...], ...]


class Command(Protocol):
    """A subcommand: `configure(parser)` adds its arguments, `run(args)` is its exit status."""

    name: str
    help: str
    run: Callable[[object], int]
    configure: Callable[[object], None] | None


class Drawing(Protocol):
    """A drawing, as a drawing=True tool and a drawing function are handed it: the
    drawing tab in front, a drawing file the call names, or the sheet being drawn."""

    def annotations(self, plugin: str) -> list[dict]:
        """Plugin `plugin`'s annotation records on the drawing."""
        ...

    def set_annotations(self, plugin: str, records: list[dict]) -> bool:
        """Put `records` in place of the plugin's annotations; in the window, one undo step."""
        ...

    def scale(self, view: str | tuple[str, int]) -> float | None:
        """A view's scale as drawn over true: a standard view by name, or a plugin view
        as (plugin, index); None for no such view."""
        ...


class Tool(Protocol):
    """An MCP tool: `call(document, arguments)` answers plain data json.dumps takes.

    With `drawing` True it is `call(document, arguments, drawing)`, handed the
    drawing tab in front, or the drawing file the call names as "drawing".
    """

    name: str
    description: str
    input_schema: Schema
    call: Callable[[Document, dict[str, object]], object]
    reads: bool
    drawing: bool


class DrawingFunction(Protocol):
    """A model.py function that works on a drawing: run for a drawing, a model's
    NAME(*args) calls `call(drawing, *args)`; run for its parts, it does nothing."""

    name: str
    call: Callable[..., object]


class Action(Protocol):
    """A window action: `run(window)` does it, or `run(window, values)` after its dialog."""

    key: str
    text: str
    run: Callable[..., None]
    icon: str | None
    shortcut: str | None
    menu: str | None
    fields: tuple[Field, ...]
    #: DX-CAD item 774: on the plugin's toolbar, and in which submenu of its menu.
    toolbar: bool
    submenu: str | None
    #: DX-CAD item 822: the command's steps, a line each, which the help shows.
    steps: tuple[str, ...]
    #: DX-CAD item 856: where it applies, some of "part", "assembly", "drawing"
    #: and "sketch"; () for everywhere.
    applies_to: tuple[str, ...]


class SheetKind(Protocol):
    """A kind of sheet part, known as "PLUGIN.NAME": `build(...)` and `unfold(part)`."""

    name: str
    build: Callable[..., SheetPart]
    unfold: Callable[[SheetPart], FlatPattern]


#: A polyline on a drawing's sheet: (x, y) points in the sheet's millimetres.
Polyline = list[tuple[float, float]]

#: A line of text on a drawing's sheet: (x, y, height, words), in millimetres.
SheetText = tuple[float, float, float, str]


class ViewKind(Protocol):
    """A kind of drawing view, "PLUGIN.NAME": `draw(document, scale, at, data)`.

    It answers the view's polylines on the sheet from the model, the scale as
    drawn over true, where the view is placed and what the drawing keeps for it;
    a shaded view answers (polylines, (png, box)), its picture an 8-bit grey or
    RGB PNG filling box, (left, bottom, right, top) in the sheet's millimetres.
    It may answer (polylines, texts), each text (x, y, height, words) as an
    annotation's, or (polylines, texts, (png, box)). A draw that takes `dpi` is
    handed None on screen and the export's dots per inch in an export.
    `dxf_image` False leaves the picture out of a DXF, its lines kept. A draw
    that takes `free` is handed the sheet's free boxes, (left, bottom, right,
    top) in mm, largest first, clear of the title block, the parts list and the
    standard views, and one that takes `sheet_name` the sheet's size, such as
    "A3" (DX-CAD item 720). `title`, such as "Detail View", is what Undo and
    Redo call one, "Add Detail View"; None for the kind's name in words
    (DX-CAD item 819). `edit(window, record)` is called on a double-click on
    one of the views or its label, and `menu` holds the entries of a
    right-click on one, (text, call), each call(window, record); `record` is
    a copy of the view's, {"kind", "at", "data"}, and window.selected_view()
    is its (plugin, index) (DX-CAD item 861). A draw taking `text_height` is
    handed the height the drawing letters in, Drawing properties' Text
    height or the sheet's own, as an annotation's draw is (DX-CAD item 868);
    a DX-CAD from before it hands it nothing.
    """

    name: str
    draw: Callable[[Document, float, tuple[float, float], dict], list[Polyline]]
    dxf_image: bool
    title: str | None
    edit: Callable[..., object] | None
    menu: tuple[tuple[str, Callable[..., object]], ...]


class AnnotationKind(Protocol):
    """A kind of drawing annotation, "PLUGIN.NAME", attached to a view by a reference.

    `resolve(document, ref)` finds the model point (x, y, z) `ref` names, every
    time the sheet is drawn, or None when it is lost; `draw(at, data)` answers
    (polylines, texts) drawn at `at` on the sheet.

    Since DX-CAD's item 704, each optional: `resolve` may answer a list of
    model points, and `draw(points, data, scale)` is then handed each one's
    sheet position and the view's scale; a `draw` taking them as keywords is
    also handed `document`, `scale` and `origin` (the view's origin on the
    sheet), and since item 720 `free` and `sheet_name`, as a view's draw
    is. `draw` may answer a third item, a dict: `{"warn": True}` draws
    it in the window's warning colour on screen only, never in an export.
    Its polylines may hold `("dimension", kind, p1, p2, line_point, text)`,
    kind "linear" or "diameter", in sheet mm: a real dimension, written to
    the DXF as a DIMENSION entity. Since DX-CAD's item 723, each optional: a
    "linear" one may take a seventh item, its rotation in degrees (0 across,
    90 up, any other aligned, DXF group 50); kind "radius" is (centre, rim,
    leader_end, text), "angular" (vertex, point on ray one, point on ray two,
    arc point, text) and "ordinate" (datum, feature, leader_end, "x" or "y",
    text), written as radial, 3-point angular and ordinate DIMENSION
    entities; and any entry may end with its text's position. On a plugin view, named by its index, a
    `resolve` taking three is handed that view's data, and its points are in
    the view's own frame, from where the view is placed, at the sheet's
    scale. `layer` "dimensions" puts what it draws on the sheet's dimension
    layer; `handles(data)` names points in the view's plane, shown on the
    selected annotation, and dragging one calls `drag(data, name, point)`
    for its new data, one undo step. A drag that cannot stand raises
    ValueError, KeyError or RuntimeError with its reason: the status bar
    says "Move Balloon failed: REASON" and nothing changes (DX-CAD item 841).

    Since DX-CAD's item 815: a `handles` or a `drag` that takes them as
    keywords is also handed `document`, `scale` and `origin`, the view's scale
    and its origin on the sheet, as `draw` is, so a point kept in sheet mm
    from the view's origin (a balloon's ring) is shown at `offset / scale`
    and a dropped `point` kept again as `point * scale`; one that takes the
    data alone is called as before. Delete (the key, or Edit > Delete) on
    the selected annotation of a kind with `handles` takes its record off
    the plugin's list, one undo step, and nothing else on the sheet moves.
    `edit(window, record)`, optional, is called on a double-click on an
    annotation of the kind with a copy of its record, so the plugin opens the
    dialog it was placed with.

    Since DX-CAD's item 763 the standard view may be "iso", the isometric
    view: its points are handed to `draw` on the sheet as any standard view's
    are, with its `origin` and `scale`, and a `draw` taking the keyword
    `outline` is handed the standard view's box on the sheet, (left, bottom,
    right, top) in mm, or None on a plugin view. dxcad.plugins.view_point(
    view, point) answers a model point in a standard view's plane.

    Since DX-CAD's item 819: `title`, such as "Balloon", is what Undo and Redo
    call one, "Move Balloon" or "Delete Balloon"; None for the kind's name in
    words. An annotation is drawn over the sheet in a layer of its own: while
    its record and the sheet under it stay as they are, `resolve` and `draw`
    are not called again, so both must answer from what they are handed.

    Since DX-CAD's item 863: a `draw` taking the keyword `views` is handed
    where every view of the sheet is now, by a standard view's name
    ("front") or a placed view's sheet name ("PLUGIN/INDEX"), each
    {"origin": (x, y), "scale": s, "box": (left, bottom, right, top)} in
    sheet mm, so a detail's connecting line can run from its circle on one
    view to the detail view itself; an annotation's record may name more
    views than its own under "views", a list of those names, and it is drawn
    again, handed their new places, whenever its own view or one it names
    is moved or rescaled. One taking `text_height` is handed the height the
    drawing letters in, Drawing properties' Text height (or the sheet's own
    when it has none), in mm. Its polylines may hold {"points": [(x, y),
    ...], "style": "thin"}, "style" one of "thin", "thick", "centre" and
    "hidden": a line of the drawing's line types, drawn on the screen, the
    PDF and the DXF as a line drawn by hand of that type is (its layer
    LINES, LINES_THICK, LINES_CENTRE or LINES_HIDDEN, with its weight).
    """

    name: str
    resolve: Callable[..., object]
    draw: Callable[..., tuple]
    layer: str | None
    handles: Callable[..., dict[str, tuple[float, float]]] | None
    drag: Callable[..., dict] | None
    edit: Callable[..., object] | None
    title: str | None


class Pick(Protocol):
    """A point picked on a drawing's sheet, snapped to the nearest drawn point within reach.

    `view` is the standard view it is in, or None; `plane` where it is in that
    view's own plane, in the model's millimetres, or None.
    """

    at: tuple[float, float]
    snapped: bool
    view: str | None
    plane: tuple[float, float] | None
    #: The last letter key pressed while the tool waits, as "H", or None (DX-CAD item 705).
    key: str | None
    #: The view's scale, drawn over true, or None off a view (DX-CAD item 715).
    scale: float | None
    #: The sheet point, in mm, the view's model origin is drawn at, as an
    #: annotation's draw is handed it, or None off a view: a point (u, v) of
    #: the view's plane is drawn at origin + scale * (u, v) (DX-CAD item 715).
    origin: tuple[float, float] | None
    #: The point clicked, before the snap, in the sheet's mm; `at` itself when
    #: the pick did not snap. Where the pointer was: for a tool that places
    #: what it draws there, where `at` is for one that measures to the model
    #: (DX-CAD item 844).
    raw: tuple[float, float] | None
    #: For a tool made with typed=True, what the user has typed while it
    #: waits, digits, "." and ":" as "4:1", or None for nothing (DX-CAD item 860).
    typed: str | None


class Unfolds(Protocol):
    """What a plugin says it unfolds: `owns(document, name)` answers whether part
    `name` is one of its own that it has a flat for, and `command` is what its
    flat command is called on its menu (DX-CAD item 828)."""

    owns: Callable[[Document, str], bool]
    command: str


class Setting(Protocol):
    """A setting a plugin keeps, "PLUGIN.NAME", and its scope, one of SCOPES:
    "document" is kept in the file and is `default` in a new one, "session"
    lasts until DX-CAD closes, "preference" is the user's across starts.
    `title` is what the user calls it (DX-CAD item 826)."""

    name: str
    title: str
    scope: str
    default: Any


class Check(Protocol):
    """A check of a drawing, "PLUGIN.NAME": `call(document, drawing_section)` answers
    lines of text, listed in the drawing tab's check panel and read again whenever
    the drawing changes; `drawing_section` is the plugin's own section of it."""

    name: str
    call: Callable[[Document, dict], list[str]]


class SheetTool(Protocol):
    """A tool on a drawing tab's right-click menu: `run(document, pick)`.

    It answers an annotation to add, {"kind", "view", "ref", "data"}, or None.

    Since DX-CAD's item 705, each optional: the tool waits for `clicks`
    clicks, and run(document, picks) is handed them all as a list when more
    than one; Escape backs out the last click, or ends the tool with none.
    While it waits, `hover(document, picks, pick)`, or `hover(document,
    pick)` when it takes two, is called as the cursor moves, with the clicks
    so far and the pick under the cursor, and the polylines it answers are
    drawn in the highlight colour, on screen only; None draws nothing. run
    may answer {"view": {"kind", "at", "data"}, "annotation": {...}}: the
    view and the annotation are added as one undo step.

    Since DX-CAD's item 763 a `run` or a `hover` that takes a keyword
    `drawing` is handed the drawing in front, a Drawing: its annotations(
    plugin) and scale(view) as the tool was armed over them. What a run sets
    with set_annotations goes on the drawing with the annotation it answers,
    in the same undo step; what a hover sets is dropped.

    Since DX-CAD's item 774 the tool is also listed on the plugin's menu, in
    `submenu` when one is named, and with `toolbar` True on the plugin's
    toolbar wearing `icon`; chosen there with a drawing tab in front it
    starts as from the right-click menu, and with none it is disabled, the
    reason its tooltip. Command search finds it by its text.

    Since DX-CAD's item 822, `steps` are what the user does once the tool is
    chosen, a line each ("Click the centre of the detail.", ...): F1 while
    the tool waits opens the help with them, the step of the next click
    marked and the steps left under it, as for DX-CAD's own commands.
    """

    key: str
    text: str
    run: Callable[..., dict | None]
    hover: Callable[..., list[Polyline] | None] | None
    clicks: int
    icon: str | None
    toolbar: bool
    submenu: str | None
    steps: tuple[str, ...]
    #: Whether the tool takes a press, a drag and a release as its two picks
    #: (DX-CAD item 846); `clicks` is then its picks in all, the two and the
    #: clicks it waits for after the release (DX-CAD item 854).
    drag: bool
    #: Whether what the user types while the tool waits is handed to it as
    #: Pick.typed (DX-CAD item 860).
    typed: bool
    #: DX-CAD item 865: where it applies, as an Action's; () for a tool that
    #: declares nothing, usable with a drawing tab in front.
    applies_to: tuple[str, ...]


class EntitlementProvider(Protocol):
    """An installed provider in ENTITLEMENT_GROUP."""

    def holds(self, entitlement: str) -> bool:
        """Whether `entitlement`, by name, is held."""
        ...


@runtime_checkable
class Registry(Protocol):
    """What a plugin's register function is handed. Every method may raise ValueError.

    A ValueError (or any exception) from register skips the plugin, said once
    on stderr; the host carries on without it.
    """

    plugin: str

    def require(self, version: int) -> None:
        """Say the plugin needs plugin API `version`; a later one than the host's skips it."""
        ...

    def require_entitlement(self, name: str, link: str | None = None) -> None:
        """Say the plugin needs entitlement `name`, which `link` says how to get.

        Without it the plugin loads locked: its toolbar and menus show, greyed,
        saying LOCKED, its tools are refused with the same words, and its model
        names and kinds of sheet part are not there. With no `link` the words
        carry DX-CAD's own buy link for the add-on, buy_link()'s (DX-CAD item
        845).
        """
        ...

    def buy_link(self, name: str | None = None) -> str:
        """DX-CAD's own buy link for an add-on, by its name, the plugin it installs
        as or its licence's product id; this plugin's own with no name. It is the
        link DX-CAD last read for that add-on, and DX-CAD's own buy link for an
        add-on it does not know (DX-CAD item 845)."""
        ...

    def add_name(self, name: str, value: object) -> None:
        """Make `value` a name every model.py starts with; `name` a public identifier."""
        ...

    def command(
        self,
        name: str,
        help: str,
        run: Callable[[object], int],
        configure: Callable[[object], None] | None = None,
    ) -> None:
        """Add `dxcad NAME`, its arguments added by `configure(parser)`."""
        ...

    def tool(
        self,
        name: str,
        description: str,
        input_schema: Schema,
        call: Callable[[Document, dict[str, object]], object],
        *,
        reads: bool = False,
        drawing: bool = False,
    ) -> None:
        """Add an MCP tool; `reads` says it changes nothing in the document, and
        `drawing` hands `call` a third argument, the Drawing it works on."""
        ...

    def drawing_function(self, name: str, call: Callable[..., object]) -> None:
        """Add model.py function `name`: run for a drawing, NAME(*args) calls
        `call(drawing, *args)` with the Drawing being drawn."""
        ...

    def action(
        self,
        key: str,
        text: str,
        run: Callable[[Window], None],
        icon: str | os.PathLike[str] | None = None,
        shortcut: str | None = None,
        menu: str | None = None,
        toolbar: bool = True,
        submenu: str | None = None,
        steps: Sequence[str] | None = None,
        applies_to: Sequence[str] | None = None,
    ) -> None:
        """Add a window action on the plugin's toolbar and menu, or on built-in `menu`.

        `icon` is an SVG or PNG file; `shortcut` a key sequence's text, such
        as "Ctrl+Shift+W"; `key` an identifier. Since DX-CAD's item 774,
        `toolbar` False keeps the action off the plugin's toolbar, and
        `submenu` names a submenu of the plugin's menu to put it in, made on
        first use, the submenus in the order first named; not with `menu`.
        Since item 822, `steps` are the command's steps, a line each, which
        the help shows for it as it shows the steps of DX-CAD's own commands.
        Since item 856, `applies_to` says where it applies, some of "part",
        "assembly", "drawing" and "sketch" (a sketch in progress), such as
        ("drawing",): with another tab in front DX-CAD greys it, its tooltip
        saying why, as it greys its own commands. None is everywhere.
        """
        ...

    def dialog(
        self,
        key: str,
        text: str,
        fields: list[Field],
        run: Callable[[Window, dict[str, object]], None],
        icon: str | os.PathLike[str] | None = None,
        shortcut: str | None = None,
        menu: str | None = None,
        toolbar: bool = True,
        submenu: str | None = None,
        applies_to: Sequence[str] | None = None,
        steps: Sequence[str] | None = None,
    ) -> None:
        """Add an action that opens a dialog of `fields` first, then runs with the values;
        since DX-CAD's item 856, `applies_to` is as action() takes it.

        Since DX-CAD's item 862, `steps` are what the user does in the dialog, a
        line each: F1 in it opens the guide with "Next steps: TEXT (step 1 of
        N)" over it, as a sheet tool's steps are shown while it waits. A DX-CAD
        from before 862 refuses `steps` here."""
        ...

    def sheet_kind(
        self,
        name: str,
        build: Callable[..., SheetPart],
        unfold: Callable[[SheetPart], FlatPattern],
    ) -> None:
        """Add a kind of sheet part, which a model makes as sheet_part("PLUGIN.NAME", ...)."""
        ...

    def view_kind(
        self,
        name: str,
        draw: Callable[[Document, float, tuple[float, float], dict], list[Polyline]],
        dxf_image: bool = True,
        title: str | None = None,
        edit: Callable[..., object] | None = None,
        menu: Sequence[tuple[str, Callable[..., object]]] | None = None,
    ) -> None:
        """Add a kind of drawing view, "PLUGIN.NAME", drawn by `draw`; `dxf_image`
        False writes a picture view's lines alone to a DXF, no IMAGE and no PNG.
        Since DX-CAD's item 819, `title` is what Undo and Redo call one, such as
        "Detail View"; the kind's name in words when not given.

        Since DX-CAD's item 861, `edit(window, record)` is called on a
        double-click on one of the views or its label, and `menu`, [(text,
        call), ...], adds an entry to the right-click menu on one for each,
        call(window, record): `record` is a copy of the view's, {"kind", "at",
        "data"}, and window.selected_view() is its (plugin, index). What
        either raises is said on the status bar. A DX-CAD from before 861
        refuses `edit` and `menu`."""
        ...

    def annotation_kind(
        self,
        name: str,
        resolve: Callable[..., object],
        draw: Callable[..., tuple],
        layer: str | None = None,
        handles: Callable[..., dict[str, tuple[float, float]]] | None = None,
        drag: Callable[..., dict] | None = None,
        edit: Callable[..., object] | None = None,
        title: str | None = None,
    ) -> None:
        """Add a kind of drawing annotation, "PLUGIN.NAME", found by `resolve`, drawn by `draw`.

        `layer`, `handles`, `drag` and, since DX-CAD's item 815, `edit` are
        optional: see AnnotationKind. Since item 819, `title` is what Undo and
        Redo call one, such as "Balloon"; the kind's name in words when not
        given.
        """
        ...

    def sheet_tool(
        self,
        key: str,
        text: str,
        run: Callable[..., dict | None],
        hover: Callable[..., list[Polyline] | None] | None = None,
        clicks: int | None = None,
        icon: str | os.PathLike[str] | None = None,
        toolbar: bool = False,
        submenu: str | None = None,
        steps: Sequence[str] | None = None,
        drag: bool = False,
        typed: bool = False,
        applies_to: Sequence[str] | None = None,
    ) -> None:
        """Add a tool to a drawing tab's right-click menu that picks on the sheet.

        Since DX-CAD's item 865, `applies_to` is as action() takes it, such as
        ("drawing",), "drawing" among the places since the tool picks on a
        sheet: with another tab in front DX-CAD greys its menu entry and
        toolbar button, the tooltip saying why, as it greys an action's. None
        is as before: usable with a drawing tab in front, disabled without one.
        A DX-CAD from before 865 refuses `applies_to`.

        Since DX-CAD's item 860, with `typed` True, what the user types while
        the tool waits, digits, "." and ":" with Backspace taking one back,
        is shown on the status bar as it is typed and handed to the tool with
        each pick, and each hover's, as Pick.typed ("4:1"); Enter takes it,
        and what is typed next starts afresh. Letters reach the tool as
        Pick.key either way. A DX-CAD from before 860 refuses `typed`.

        Since DX-CAD's item 846, with `drag` True the tool takes a press, a
        drag and a release: run(document, picks) is handed the press and the
        release as its two picks, and the moves between them go to `hover`.

        Since DX-CAD's item 854 a drag tool given `clicks` waits for that
        many clicks after the release: `drag=True, clicks=1` is a drag and
        then one click, and run(document, picks) is handed the press, the
        release and the click, in that order; `hover` is called throughout.
        Escape while the button is held, or after the release, takes the
        whole drag back, and after a click that click; nothing is made until
        the last. Given no `clicks`, or 0, the tool is the press and the
        release alone. A DX-CAD from before 854 takes `clicks=1` with `drag`
        as none, and refuses any other.

        Since DX-CAD's item 822, `steps` are what the user does once the tool
        is chosen, a line each: F1 while it waits shows them, the one the
        user is on marked.

        `hover` and `clicks` are optional: see SheetTool. Since DX-CAD's item
        774 the tool is listed on the plugin's menu too, in `submenu` when one
        is named, and with `toolbar` True on the plugin's toolbar wearing
        `icon`, an SVG or PNG file.
        """
        ...

    def unfolds(self, owns: Callable[[Document, str], bool], command: str) -> None:
        """Say which parts the plugin unfolds and with which of its commands:
        `owns(document, name)` answers whether part `name` is one of them, and
        `command` is what its flat command is called on its menu, "Flat Pattern".
        DX-CAD's own Flat Pattern, picked for one, then says "NAME was made by
        PLUGIN: use PLUGIN > COMMAND" (DX-CAD item 828)."""
        ...

    def drawing_ready(self, call: Callable[[Document, object], object]) -> None:
        """Work the plugin's tools would do at their first use, done as a drawing opens:
        `call(document, drawing)` is made once a drawing tab has opened and drawn its
        sheet, with the Document its tools, hovers and annotations are handed later
        and the drawing as a sheet tool's run is, and again when the model changes,
        not when only the annotations do. It runs as part of the opening, so what it
        keeps (by document.revision) is there before the first click; what it raises
        is said on the status bar and the drawing opens (DX-CAD item 864). A DX-CAD
        from before 864 has no drawing_ready: call it when hasattr(registry,
        "drawing_ready")."""
        ...

    def setting(self, name: str, title: str, scope: str, default: object = None) -> None:
        """Declare a setting the plugin keeps, "PLUGIN.NAME", and its scope, one of
        SCOPES. `default`, plain data, is what it is until set. The window keeps
        it where the scope says: window.plugin_setting(plugin, name) reads it and
        window.set_plugin_setting(plugin, name, value) writes it (DX-CAD item 826)."""
        ...

    def check(self, name: str, call: Callable[[Document, dict], list[str]]) -> None:
        """Add a check of a drawing, "PLUGIN.NAME", listed in the drawing tab's panel."""
        ...
