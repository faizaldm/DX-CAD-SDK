<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Designmatix Ltd -->
# DX-CAD SDK

Everything needed to build on DX-CAD, under the Apache License 2.0:

- **The plugin API** (`dxcad_sdk.plugin`): the protocols and constants a
  plugin meets. A plugin adds model names, subcommands, MCP tools for agents,
  window actions and dialogs, kinds of sheet part that unfold through DX-CAD's
  flat pipeline, its own section of a saved file, and may say it needs an
  entitlement.
- **Type stubs** (`dxcad-stubs`): every function and class a DX-CAD model.py
  starts with, so an editor completes and checks a model.
- **A checker**: `dxcad-sdk check PATH` checks an add-on's declarations
  before DX-CAD loads it, one line per check.
- **A sweep**: `dxcad-sdk sweep NAME` runs DX-CAD's command sweep on an
  installed add-on's commands: each opened offscreen, its dialogs checked on
  a 1366 x 768 screen at 100, 125 and 150 percent and the parts it builds
  checked valid (DX-CAD installed beside it; see DX-CAD's docs/plugins.md).
- **Examples and a template**: three example plugins under `examples/` and a
  starter under `template/`.
- **Docs**: `docs/agents.md` (DX-CAD with Claude and other MCP clients, every
  tool's inputs, example prompts) and `docs/format.md` (the .dxcprt, .dxcasm and
  .dxcdrg file formats, and how older files open).

The SDK holds interfaces, stubs, docs and examples only. DX-CAD itself is
installed apart and is not part of the SDK or licensed by it (see NOTICE).

## A first plugin

Copy `template/` to a folder of your own, rename `dxcad_myplugin`, then:

    dxcad-sdk check my-plugin
    python -m pip install -e my-plugin

and start DX-CAD: the plugin's names, tools and actions are there. A plugin
that draws on drawings registers view kinds, annotation kinds and sheet tools
(`registry.view_kind`, `registry.annotation_kind`, `registry.sheet_tool`; see
`dxcad_sdk.plugin` and the plugins page of the docs). Anything a
plugin takes from DX-CAD (`from dxcad.model import ...`) is imported inside
the functions that use it, so the checker can import the plugin without
DX-CAD.

## What an add-on may import

The installed DX-CAD runs an add-on in its own Python, which carries only
what it was built with. An add-on may import there, at the top of a module
or inside a function alike: any OCP module, such as `OCP.BRepLProp`; any
module of the Python standard library, but `tkinter` and what is built on it
(`turtle`, `turtledemo`, `idlelib`), `test`, `ensurepip` and `venv`, and on
Windows `curses`, `pty`, `tty` and `crypt`; these Qt modules of PySide6:
`QtCore`, `QtGui`, `QtWidgets`, `QtSvg`, `QtSvgWidgets`, `QtNetwork`,
`QtPrintSupport`, `QtOpenGL`, `QtOpenGLWidgets` and `QtPdf`; and nothing
outside DX-CAD's own dependencies (cadquery-ocp, PySide6 and cryptography)
unless the add-on's wheel carries it. `dxcad doctor --addons` imports every
installed add-on's modules with these and names each that fails.
