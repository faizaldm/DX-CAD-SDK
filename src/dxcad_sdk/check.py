# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""dxcad-sdk check PATH: an add-on's declarations, checked before DX-CAD loads it.

PATH is the add-on's project folder, the one holding its pyproject.toml. The
check reads the entry points it declares in the dxcad.plugins group, imports
each one's module from PATH (or PATH/src), and runs its register function
against a Recorder, a registry of the SDK's own that keeps what it is given
and holds each thing to the rules DX-CAD loads a plugin by. One line is said
for each check, "ok" or "FAIL" with what is wrong; the exit status is 0 only
when every line is ok.

DX-CAD itself is not needed: a plugin's module is imported, so anything it
takes from DX-CAD belongs inside the functions that use it, where it is
imported when DX-CAD calls them.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import re
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

from dxcad_sdk.plugin import (
    API_VERSION,
    ENTITLEMENT_GROUP,
    ENTRY_POINT_GROUP,
    MODEL_CALLS,
    PLUGIN_FUNCTIONS,
    PRIVATE_MODULES,
    SCOPES,
    WINDOW_CALLS,
)

#: An entry point's value: "module:attribute", the module dotted.
ENTRY_VALUE = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*:\s*([A-Za-z_]\w*)\s*$")

#: What an MCP tool may be called.
TOOL_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")

#: What an action's icon may be.
ICON_SUFFIXES = (".svg", ".png")

#: Where a command may say it applies (DX-CAD item 856): the kind of tab in
#: front, or a sketch in progress.
APPLIES_TO = ("part", "assembly", "drawing", "sketch")

#: DX-CAD's toolbar icons are this many pixels at 100 percent, and the window
#: is checked at these display ratios (DX-CAD item 729): an icon must draw at
#: each without being scaled up from a smaller picture, which an SVG with a
#: viewBox always does and a PNG does while it is at least the largest size.
ICON_PIXELS = 24
ICON_RATIOS = (1.5, 2.0)
SVG_TAG = "{http://www.w3.org/2000/svg}svg"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def icon_problems(path: Path) -> list[str]:
    """What stops the icon at `path` drawing sharp at ICON_RATIOS, the core's own check
    (DX-CAD item 774): an SVG parses and has a viewBox; a PNG is large enough."""
    if path.suffix.lower() == ".svg":
        try:
            root = ElementTree.parse(path).getroot()
        except (ElementTree.ParseError, OSError) as error:
            return [f"does not parse as SVG: {error}"]
        if root.tag not in (SVG_TAG, "svg"):
            return [f"is not an SVG document; its root is {root.tag!r}"]
        if not (root.get("viewBox") or "").strip():
            return ["has no viewBox, so it cannot be drawn at 150 and 200 percent unscaled"]
        return []
    try:
        with open(path, "rb") as file:
            head = file.read(24)
    except OSError as error:
        return [f"cannot be read: {error}"]
    if not head.startswith(PNG_SIGNATURE) or head[12:16] != b"IHDR":
        return ["is not a PNG"]
    width = int.from_bytes(head[16:20], "big")
    height = int.from_bytes(head[20:24], "big")
    wanted = round(ICON_PIXELS * max(ICON_RATIOS))
    if min(width, height) < wanted:
        return [
            f"is {width} x {height} px: a toolbar icon is {ICON_PIXELS} px, so at "
            f"{round(max(ICON_RATIOS) * 100)} percent it needs {wanted}; use an SVG or a larger PNG"
        ]
    return []


@dataclass
class Recorder:
    """A registry that keeps what a plugin registers and every rule it breaks."""

    plugin: str
    base: Path = field(default_factory=Path.cwd)
    problems: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    sheet_kinds: list[str] = field(default_factory=list)
    view_kinds: list[str] = field(default_factory=list)
    annotation_kinds: list[str] = field(default_factory=list)
    sheet_tools: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)
    drawing_functions: list[str] = field(default_factory=list)
    #: DX-CAD item 826: each setting declared, and its scope.
    settings: list[str] = field(default_factory=list)
    entitlement: tuple[str, str] | None = None
    api: int | None = None
    #: Each icon given, as (what it is of, its file), for the icon checks (item 774).
    icons: list[tuple[str, Path]] = field(default_factory=list)
    #: Sheet tool keys as given, to find one an action has (item 774).
    tool_keys: list[str] = field(default_factory=list)

    def _fail(self, said: str) -> None:
        self.problems.append(said)

    def _icon(self, what: str, key: str, icon: object) -> None:
        """Hold `icon` to being an SVG or PNG file, and keep it for the icon checks."""
        if icon is None:
            return
        where = Path(icon) if Path(icon).is_absolute() else self.base / icon
        if Path(icon).is_file():
            where = Path(icon)
        if not where.is_file():
            self._fail(f"{what} {key!r} names an icon that is not there: {icon}")
        elif where.suffix.lower() not in ICON_SUFFIXES:
            self._fail(f"{what} {key!r}: an icon is an SVG or a PNG, not {where.name}")
        else:
            self.icons.append((f"{what} {key!r}", where))

    def _placing(self, what: str, key: str, toolbar: object, menu, submenu) -> None:
        """Hold toolbar and submenu to the rules DX-CAD loads them by (item 774)."""
        if not isinstance(toolbar, bool):
            self._fail(f"{what} {key!r}: toolbar is True or False, got {toolbar!r}")
        if submenu is not None and (not isinstance(submenu, str) or not submenu.strip()):
            self._fail(f"{what} {key!r} names a submenu that is not text: {submenu!r}")
        if submenu is not None and menu is not None:
            self._fail(
                f"{what} {key!r} names a built-in menu and a submenu of the plugin's own; "
                "one or the other"
            )

    def _once(self, kept: list[str], what: str, name: str) -> None:
        if name in kept:
            self._fail(f"{what} {name!r} is registered twice")
        kept.append(name)

    def require(self, version: int) -> None:
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            self._fail(f"require({version!r}): a plugin API version is a whole number from 1")
        elif version > API_VERSION:
            self._fail(f"require({version}): this SDK describes plugin API {API_VERSION}")
        else:
            self.api = version

    def require_entitlement(self, name: str, link: str | None = None) -> None:
        given = (("name", name),) if link is None else (("name", name), ("link", link))
        for said, value in given:
            if not isinstance(value, str) or not value.strip():
                self._fail(f"an entitlement's {said} is text, got {value!r}")
                return
        self.entitlement = (name.strip(), "" if link is None else link.strip())

    def buy_link(self, name: str | None = None) -> str:
        # The host answers its own link; a check has no host to ask.
        return ""

    def add_name(self, name: str, value: object) -> None:
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
            self._fail(f"model name {name!r} is not a public identifier")
            return
        self._once(self.names, "model name", name)

    def command(
        self,
        name: str,
        help: str,
        run: Callable[[object], int],
        configure: Callable[[object], None] | None = None,
    ) -> None:
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            self._fail(f"command {name!r} is not a lower-case word")
            return
        if not callable(run) or (configure is not None and not callable(configure)):
            self._fail(f"command {name!r} needs a run (and a configure, if any) to call")
        self._once(self.commands, "command", name)

    def tool(
        self,
        name: str,
        description: str,
        input_schema: dict,
        call: Callable,
        *,
        reads: bool = False,
        drawing: bool = False,
    ) -> None:
        if not isinstance(name, str) or not TOOL_NAME.match(name):
            self._fail(f"tool {name!r} is not a tool name (letters, digits, _ and -)")
            return
        if not isinstance(drawing, bool):
            self._fail(f"tool {name!r}: drawing is True or False, got {drawing!r}")
        elif callable(call) and not takes(call, 3 if drawing else 2):
            wanted = "(document, arguments, drawing)" if drawing else "(document, arguments)"
            self._fail(f"tool {name!r}: its call does not take {wanted}")
        if not isinstance(description, str) or not description.strip():
            self._fail(f"tool {name!r} has no description")
        for problem in schema_problems(input_schema):
            self._fail(f"tool {name!r}: {problem}")
        if not callable(call):
            self._fail(f"tool {name!r} has no call to make")
        if not isinstance(reads, bool):
            self._fail(f"tool {name!r}: reads is True or False, got {reads!r}")
        self._once(self.tools, "tool", name)

    def _steps(self, what: str, key, steps) -> None:
        # DX-CAD item 822: a command's steps, each a line of words.
        if steps is None:
            return
        if isinstance(steps, str) or not all(
            isinstance(step, str) and step.strip() and "\n" not in step for step in steps
        ):
            self._fail(f"{what} {key!r}: its steps are lines of words, got {steps!r}")

    def action(
        self,
        key,
        text,
        run,
        icon=None,
        shortcut=None,
        menu=None,
        toolbar=True,
        submenu=None,
        steps=None,
        applies_to=None,
    ) -> None:
        if not isinstance(key, str) or not key.isidentifier():
            self._fail(f"action key {key!r} is not an identifier")
            return
        self._steps("action", key, steps)
        self._applies("action", key, applies_to)
        if not isinstance(text, str) or not text.strip():
            self._fail(f"action {key!r} has no text")
        if not callable(run):
            self._fail(f"action {key!r} has nothing to run")
        self._icon("action", key, icon)
        for said, value in (("shortcut", shortcut), ("menu", menu)):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                self._fail(f"action {key!r} names a {said} that is not text: {value!r}")
        self._placing("action", key, toolbar, menu, submenu)
        self._once(self.actions, "action", key)

    def dialog(
        self,
        key,
        text,
        fields,
        run,
        icon=None,
        shortcut=None,
        menu=None,
        toolbar=True,
        submenu=None,
        applies_to=None,
        steps=None,
    ) -> None:
        if not fields:
            self._fail(f"dialog {key!r} has no fields")
        for one in fields or ():
            if not isinstance(one, tuple | list) or len(one) != 3:
                self._fail(f"dialog {key!r} has a field that is not (name, label, default)")
                continue
            name, _, default = one
            if not str(name).isidentifier():
                self._fail(f"dialog {key!r}: field name {name!r} is not an identifier")
            if isinstance(default, bool) or not isinstance(default, int | float | str):
                self._fail(f"field {name!r} of dialog {key!r} has no number or text default")
        # DX-CAD item 862: the steps F1 in the dialog shows.
        self.action(
            key, text, run, icon, shortcut, menu, toolbar, submenu, steps, applies_to=applies_to
        )

    def _applies(self, what: str, key: str, applies_to) -> None:
        """Hold applies_to to what DX-CAD loads (item 856): None, or a tuple of some of
        "part", "assembly", "drawing" and "sketch"."""
        if applies_to is None:
            return
        if (
            isinstance(applies_to, str)
            or not applies_to
            or not all(one in APPLIES_TO for one in applies_to)
        ):
            self._fail(
                f"{what} {key!r} applies to some of {', '.join(APPLIES_TO)}, "
                f"as a tuple, not {applies_to!r}"
            )

    def sheet_kind(self, name: str, build: Callable, unfold: Callable) -> None:
        if not isinstance(name, str) or not name.isidentifier():
            self._fail(f"sheet part kind {name!r} is not an identifier")
            return
        if not callable(build) or not callable(unfold):
            self._fail(f"sheet part kind {name!r} needs a build and an unfold to call")
        self._once(self.sheet_kinds, "sheet part kind", f"{self.plugin}.{name}")

    def _hook(self, kept: list[str], what: str, name: object, *calls: object) -> None:
        if not isinstance(name, str) or not name.isidentifier():
            self._fail(f"{what} {name!r} is not an identifier")
            return
        if not all(callable(call) for call in calls):
            self._fail(f"{what} {name!r} is given something it cannot call")
        self._once(kept, what, f"{self.plugin}.{name}")

    def _title(self, what: str, name: str, title: object) -> None:
        # DX-CAD item 819: what Undo and Redo call one of the kind, in words.
        if title is not None and (not isinstance(title, str) or not title.strip()):
            self._fail(f"{what} {name!r}: its title is words, or not given, got {title!r}")

    def view_kind(
        self,
        name: str,
        draw: Callable,
        dxf_image: bool = True,
        title: str | None = None,
        edit: Callable | None = None,
        menu=None,
    ) -> None:
        if not isinstance(dxf_image, bool):
            self._fail(f"view kind {name!r}: dxf_image is True or False, got {dxf_image!r}")
        self._title("view kind", name, title)
        if callable(draw) and not takes(draw, 4):
            self._fail(f"view kind {name!r}: its draw does not take (document, scale, at, data)")
        # DX-CAD item 861: edit(window, record), and the right-click entries.
        if edit is not None and not (callable(edit) and takes(edit, 2)):
            self._fail(f"view kind {name!r}: its edit does not take (window, record)")
        given = [] if menu is None else list(menu)
        for entry in given:
            fine = isinstance(entry, (tuple, list)) and len(entry) == 2
            if not fine or not isinstance(entry[0], str) or not entry[0].strip():
                self._fail(f"view kind {name!r} needs its menu as (text, call) pairs")
            elif not (callable(entry[1]) and takes(entry[1], 2)):
                self._fail(
                    f"view kind {name!r}: menu entry {entry[0]!r} does not take (window, record)"
                )
        self._hook(self.view_kinds, "view kind", name, draw)

    def unfolds(self, owns: Callable, command: str) -> None:
        # DX-CAD item 828: which parts the plugin unfolds, and its command.
        if not callable(owns):
            self._fail("unfolds: its first argument is not something to call")
        elif not takes(owns, 2):
            self._fail("unfolds: its call does not take (document, name)")
        if not isinstance(command, str) or not command.strip():
            self._fail(f"unfolds: its command's name is words, got {command!r}")

    def drawing_ready(self, call: Callable) -> None:
        # DX-CAD item 864: call(document, drawing), made as a drawing opens.
        if not callable(call):
            self._fail("drawing_ready: its argument is not something to call")
        elif not takes(call, 2):
            self._fail("drawing_ready: its call does not take (document, drawing)")

    def setting(self, name: str, title: str, scope: str, default: object = None) -> None:
        # DX-CAD item 826: a setting says how long it is kept.
        if not isinstance(title, str) or not title.strip():
            self._fail(f"setting {name!r} needs a title, got {title!r}")
        if scope not in SCOPES:
            self._fail(
                f"setting {name!r}: a scope is one of {', '.join(SCOPES)}, got {scope!r}"
            )
        self._hook(self.settings, "setting", name)

    def check(self, name: str, call: Callable) -> None:
        if callable(call) and not takes(call, 2):
            self._fail(f"check {name!r}: its call does not take (document, drawing_section)")
        self._hook(self.checks, "check", name, call)

    def drawing_function(self, name: str, call: Callable) -> None:
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
            self._fail(f"drawing function {name!r} is not a public identifier")
            return
        if not callable(call):
            self._fail(f"drawing function {name!r} is given something it cannot call")
        elif not takes_first(call):
            self._fail(f"drawing function {name!r}: its call does not take (drawing, ...)")
        self._once(self.drawing_functions, "drawing function", name)

    def annotation_kind(
        self,
        name: str,
        resolve: Callable,
        draw: Callable,
        layer: str | None = None,
        handles: Callable | None = None,
        drag: Callable | None = None,
        edit: Callable | None = None,
        title: str | None = None,
    ) -> None:
        if layer not in (None, "dimensions"):
            self._fail(f"annotation kind {name!r} is drawn on its own layer or 'dimensions'")
        self._title("annotation kind", name, title)
        if (handles is None) != (drag is None):
            self._fail(f"annotation kind {name!r} needs handles and a drag, or neither")
        # DX-CAD item 815: edit(window, record), called on a double-click.
        given = [call for call in (handles, drag, edit) if call is not None]
        self._hook(self.annotation_kinds, "annotation kind", name, resolve, draw, *given)

    def sheet_tool(
        self,
        key: str,
        text: str,
        run: Callable,
        hover: Callable | None = None,
        clicks: int | None = None,
        icon=None,
        toolbar: bool = False,
        submenu: str | None = None,
        steps=None,
        drag: bool = False,
        typed: bool = False,
        applies_to=None,
    ) -> None:
        if not isinstance(text, str) or not text.strip():
            self._fail(f"sheet tool {key!r} has no text")
        self._applies("sheet tool", key, applies_to)
        known = applies_to and not isinstance(applies_to, str)
        if known and all(one in APPLIES_TO for one in applies_to) and "drawing" not in applies_to:
            # DX-CAD item 865: a sheet tool picks on a sheet.
            self._fail(f"sheet tool {key!r} picks on a sheet: its places need 'drawing'")
        if not isinstance(typed, bool):
            # DX-CAD item 860: True or False, whether the tool takes typed input.
            self._fail(f"sheet tool {key!r} takes typed=True or False, not {typed!r}")
        self._steps("sheet tool", key, steps)
        if clicks is None:
            clicks = 0 if drag else 1
        whole = isinstance(clicks, int) and not isinstance(clicks, bool)
        if drag and (not whole or clicks < 0):
            # DX-CAD's item 854: a drag, then the clicks after its release.
            self._fail(
                f"sheet tool {key!r} takes a press and a release, then 0 clicks or more, "
                f"not {clicks!r}"
            )
        if not drag and (not whole or clicks < 1):
            self._fail(f"sheet tool {key!r} waits for 1 click or more, not {clicks!r}")
        self._icon("sheet tool", key, icon)
        self._placing("sheet tool", key, toolbar, None, submenu)
        if isinstance(key, str):
            self.tool_keys.append(key)
        given = [] if hover is None else [hover]
        self._hook(self.sheet_tools, "sheet tool", key, run, *given)

    def clashes(self) -> list[str]:
        """Each sheet tool key an action of the plugin has too (item 774): in the window
        both would be one action, so DX-CAD lists the tool on the sheet's menu alone."""
        return [key for key in self.tool_keys if key in self.actions]

    def registered(self) -> int:
        """How many things it was given."""
        kept = (
            self.names,
            self.commands,
            self.tools,
            self.actions,
            self.sheet_kinds,
            self.view_kinds,
            self.annotation_kinds,
            self.sheet_tools,
            self.checks,
            self.drawing_functions,
            self.settings,
        )
        return sum(len(one) for one in kept)


def takes(call: Callable, count: int) -> bool:
    """Whether `call` can be called with `count` positional arguments: True when its
    signature cannot be read, as a built-in's sometimes cannot."""
    try:
        signature = inspect.signature(call)
    except (TypeError, ValueError):
        return True
    try:
        signature.bind(*range(count))
    except TypeError:
        return False
    return True


def takes_first(call: Callable) -> bool:
    """Whether `call` takes a first positional argument, whatever else it needs: one
    positional parameter at least, or *args (DX-CAD item 763). A drawing function is
    called (drawing, *args) with the model's own arguments, so label(drawing, part,
    words) is one. True when its signature cannot be read."""
    try:
        parameters = inspect.signature(call).parameters.values()
    except (TypeError, ValueError):
        return True
    kinds = inspect.Parameter
    positional = (kinds.POSITIONAL_ONLY, kinds.POSITIONAL_OR_KEYWORD, kinds.VAR_POSITIONAL)
    return any(one.kind in positional for one in parameters)


def schema_problems(schema: object) -> list[str]:
    """What is wrong with an MCP tool's input schema, as DX-CAD and a client read it."""
    if not isinstance(schema, dict):
        return ["its input schema is not a JSON object"]
    found = []
    if schema.get("type") != "object":
        found.append('its input schema\'s "type" is not "object"')
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return [*found, 'its input schema\'s "properties" is not an object']
    for name, one in properties.items():
        if not isinstance(one, dict):
            found.append(f"input {name!r} has no schema of its own")
    required = schema.get("required", [])
    if not isinstance(required, list):
        found.append('its input schema\'s "required" is not a list')
    else:
        for name in required:
            if name not in properties:
                found.append(f"input {name!r} is required but not among the properties")
    return found


@dataclass
class Line:
    """One line of the report."""

    ok: bool
    said: str
    #: A line that fails nothing but says what to change (DX-CAD item 760).
    warning: bool = False

    def __str__(self) -> str:
        mark = "WARN" if self.warning else ("ok  " if self.ok else "FAIL")
        return f"{mark}  {self.said}"


def _entry_points(project: dict) -> dict[str, dict[str, str]]:
    found = project.get("entry-points", {})
    return found if isinstance(found, dict) else {}


def _module_root(folder: Path, module: str) -> Path | None:
    """The folder `module` imports from: PATH or PATH/src, whichever holds it."""
    parts = module.split(".")
    for root in (folder, folder / "src"):
        here = root.joinpath(*parts)
        if here.with_suffix(".py").is_file() or (here / "__init__.py").is_file():
            return root
    return None


def _imported(root: Path, module: str):
    """`module` imported from `root`, and taken out of sys.modules again after."""
    before = set(sys.modules)
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    try:
        return importlib.import_module(module)
    finally:
        sys.path.remove(str(root))
        for name in set(sys.modules) - before:
            if name == module or name.startswith(module.split(".")[0]):
                sys.modules.pop(name, None)


def check(path: str | Path) -> list[Line]:
    """Every line of the report for the add-on at `path`."""
    folder = Path(path)
    pyproject = folder / "pyproject.toml"
    if not pyproject.is_file():
        return [Line(False, f"{folder} has no pyproject.toml; give the add-on's project folder")]
    try:
        project = tomllib.loads(pyproject.read_text(encoding="utf-8")).get("project", {})
    except tomllib.TOMLDecodeError as error:
        return [Line(False, f"pyproject.toml does not parse: {error}")]
    lines = []
    for key in ("name", "version"):
        given = project.get(key)
        lines.append(
            Line(True, f"project {key} is {given!r}")
            if isinstance(given, str) and given.strip()
            else Line(False, f"pyproject.toml's [project] has no {key}")
        )
    groups = _entry_points(project)
    entries = groups.get(ENTRY_POINT_GROUP, {})
    providers = groups.get(ENTITLEMENT_GROUP, {})
    if not entries and not providers:
        lines.append(Line(False, f'no entry point in the "{ENTRY_POINT_GROUP}" group'))
        return lines
    for name, value in providers.items():
        lines.append(_check_provider(folder, name, value))
    for name, value in entries.items():
        lines += _check_plugin(folder, name, value)
    return lines


def _target(folder: Path, name: str, value: object) -> tuple[object, Line]:
    """What entry `name` = `value` names, loaded, and its line; None where it cannot be."""
    match = ENTRY_VALUE.match(value) if isinstance(value, str) else None
    if match is None:
        return None, Line(False, f"entry {name!r} = {value!r} is not 'module:attribute'")
    module, attribute = match.groups()
    root = _module_root(folder, module)
    if root is None:
        return None, Line(False, f"entry {name!r}: module {module!r} is not under {folder}")
    try:
        loaded = getattr(_imported(root, module), attribute)
    except Exception as error:  # noqa: BLE001 - a plugin's own fault, reported
        return None, Line(False, f"entry {name!r}: {module}:{attribute} does not load: {error!r}")
    return loaded, Line(True, f"entry {name!r} loads {module}:{attribute}")


def _check_provider(folder: Path, name: str, value: object) -> Line:
    provider, line = _target(folder, name, value)
    if provider is None:
        return line
    holds = getattr(provider, "holds", provider)
    if not callable(holds):
        return Line(False, f"entitlement provider {name!r} is not callable and has no holds")
    return Line(True, f"entitlement provider {name!r} can be asked")


def _sources(folder: Path, module: str) -> list[Path]:
    """The .py files of the top-level package or module `module` is in, under `folder`."""
    top = module.split(".")[0]
    root = _module_root(folder, top)
    if root is None:
        return []
    package = root / top
    if package.is_dir():
        return sorted(package.rglob("*.py"))
    single = package.with_suffix(".py")
    return [single] if single.is_file() else []


def plugin_api_names(source: str, module: str = "plugins") -> list[str]:
    """Every name `source` takes from dxcad.plugins: imported from it, or read off it.
    With `module` "model", from dxcad.model instead (DX-CAD item 762)."""
    tree = ast.parse(source)
    found: list[str] = []
    module_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == f"dxcad.{module}":
            found += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module == "dxcad":
            module_names |= {
                alias.asname or alias.name for alias in node.names if alias.name == module
            }
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == f"dxcad.{module}" and alias.asname:
                    module_names.add(alias.asname)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        owner = node.value
        if isinstance(owner, ast.Name) and owner.id in module_names:
            found.append(node.attr)
        elif (
            isinstance(owner, ast.Attribute)
            and owner.attr == module
            and isinstance(owner.value, ast.Name)
            and owner.value.id == "dxcad"
        ):
            found.append(node.attr)
    return found


#: The modules of DX-CAD a plugin may import: the plugin API and the model language.
PUBLIC_MODULES = ("dxcad.plugins", "dxcad.model")


def core_imports(source: str) -> list[str]:
    """The modules of DX-CAD beyond PUBLIC_MODULES that `source` imports, once each, in order
    (DX-CAD item 760)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names = [node.module]
            if node.module == "dxcad":
                names = [f"dxcad.{alias.name}" for alias in node.names]
        else:
            continue
        for module in names:
            inside = module.startswith("dxcad.") and module not in PUBLIC_MODULES
            if inside and not module.startswith(tuple(f"{one}." for one in PUBLIC_MODULES)):
                if module not in found:
                    found.append(module)
    return found


def _private_lines(name: str, modules: list[str]) -> list[Line]:
    """A warning naming each of DX-CAD's own modules the plugin imports, and what to use."""
    lines = []
    for module in modules:
        instead = PRIVATE_MODULES.get(module, "only dxcad.plugins and dxcad.model")
        lines.append(
            Line(
                True,
                f"plugin {name!r} imports {module}, which is not the plugin API: use {instead}",
                warning=True,
            )
        )
    return lines


def window_calls(source: str) -> list[str]:
    """What `source` reads off a name `window`, the window an action is handed, once
    each, in order (DX-CAD item 761)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        owner = node.value if isinstance(node, ast.Attribute) else None
        if isinstance(owner, ast.Name) and owner.id == "window" and node.attr not in found:
            found.append(node.attr)
    return found


def _window_lines(name: str, calls: list[str]) -> list[Line]:
    """An ok line naming the window's calls the plugin uses, and a warning for each the
    SDK's Window has not got."""
    known = [call for call in calls if call in WINDOW_CALLS]
    lines = []
    if known:
        said = ", ".join(f"window.{call}" for call in known)
        lines.append(Line(True, f"plugin {name!r} calls {said}"))
    for call in calls:
        if call not in WINDOW_CALLS:
            said = f"plugin {name!r} reads window.{call}, which the SDK's Window has not got"
            lines.append(Line(True, said, warning=True))
    return lines


def _api_lines(folder: Path, name: str, value: str) -> list[Line]:
    """A FAIL for each name the plugin takes from dxcad.plugins that the plugin API has not
    got (DX-CAD item 759), and one ok line naming the ones it takes."""
    match = ENTRY_VALUE.match(value) if isinstance(value, str) else None
    if match is None:
        return []
    used: set[str] = set()
    model: set[str] = set()
    private: list[str] = []
    calls: list[str] = []
    for path in _sources(folder, match.group(1)):
        try:
            source = path.read_text(encoding="utf-8")
            used |= set(plugin_api_names(source))
            model |= set(plugin_api_names(source, "model"))
            private += [one for one in core_imports(source) if one not in private]
            calls += [one for one in window_calls(source) if one not in calls]
        except (SyntaxError, UnicodeDecodeError) as error:
            return [Line(False, f"plugin {name!r}: {path.name} does not parse: {error}")]
    lines = [
        Line(False, f"plugin {name!r} takes {each} from dxcad.plugins, which the plugin API "
                    "has not got")
        for each in sorted(used - set(PLUGIN_FUNCTIONS))
    ]
    known = sorted(used & set(PLUGIN_FUNCTIONS))
    if known:
        lines.append(Line(True, f"plugin {name!r} takes {', '.join(known)} from dxcad.plugins"))
    own = sorted(model & set(MODEL_CALLS))
    if own:
        lines.append(Line(True, f"plugin {name!r} calls {', '.join(own)} of dxcad.model"))
    return lines + _private_lines(name, private) + _window_lines(name, calls)


def _icon_lines(name: str, recorder: Recorder) -> list[Line]:
    """One line per icon (item 774): the core's own check, that it draws at 150 and 200
    percent without being scaled up, light and dark theme alike (the toolbars keep
    the platform's palette in both)."""
    lines = []
    for what, path in recorder.icons:
        problems = icon_problems(path)
        if problems:
            lines += [Line(False, f"plugin {name!r}: icon {path.name} of {what} {said}")
                      for said in problems]
        else:
            lines.append(
                Line(
                    True,
                    f"plugin {name!r}: icon {path.name} of {what} draws at 150 and 200 percent "
                    "in both themes",
                )
            )
    return lines


def _check_plugin(folder: Path, name: str, value: object) -> list[Line]:
    register, line = _target(folder, name, value)
    if register is None:
        return [line]
    lines = [line]
    if not callable(register):
        register = getattr(register, "register", None)
    if not callable(register):
        return [*lines, Line(False, f"plugin {name!r}: what it names is not a register function")]
    recorder = Recorder(name, folder)
    try:
        register(recorder)
    except Exception as error:  # noqa: BLE001 - a plugin's own fault, reported
        return [*lines, Line(False, f"plugin {name!r}: register raised {error!r}")]
    lines += [Line(False, f"plugin {name!r}: {problem}") for problem in recorder.problems]
    lines += [
        Line(
            False,
            f"plugin {name!r}: sheet tool {key!r} has an action's key, so DX-CAD would list "
            "it on the sheet's right-click menu alone",
        )
        for key in recorder.clashes()
    ]
    lines += _icon_lines(name, recorder)
    if recorder.registered() == 0:
        lines.append(Line(False, f"plugin {name!r} registers nothing"))
    if not recorder.problems and recorder.registered():
        kinds = [
            f"{len(kept)} {what}"
            for what, kept in (
                ("model names", recorder.names),
                ("commands", recorder.commands),
                ("tools", recorder.tools),
                ("actions", recorder.actions),
                ("sheet part kinds", recorder.sheet_kinds),
                ("view kinds", recorder.view_kinds),
                ("annotation kinds", recorder.annotation_kinds),
                ("sheet tools", recorder.sheet_tools),
                ("checks", recorder.checks),
                ("drawing functions", recorder.drawing_functions),
            )
            if kept
        ]
        lines.append(Line(True, f"plugin {name!r} registers {', '.join(kinds)}"))
    return lines + _api_lines(folder, name, value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dxcad-sdk", description="The DX-CAD SDK's tools.")
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("check", help="check an add-on's declarations")
    one.add_argument("path", help="the add-on's project folder, holding its pyproject.toml")
    swept = commands.add_parser(
        "sweep", help="run DX-CAD's command sweep on an installed add-on's commands"
    )
    swept.add_argument("name", help="the add-on's plugin name, as its entry point gives it")
    swept.add_argument(
        "--known", type=Path, help="failures the add-on knows of, one KEY: CHECK a line"
    )
    args = parser.parse_args(argv)
    if args.command == "sweep":
        from dxcad_sdk import sweep

        return sweep.run(args.name, args.known)
    lines = check(args.path)
    for line in lines:
        print(line)
    failed = sum(not line.ok for line in lines)
    warned = sum(line.warning for line in lines)
    said = f"{len(lines) - failed - warned} ok, {failed} failed"
    print(said + (f", {warned} warnings" if warned else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
