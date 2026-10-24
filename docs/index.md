# DX-CAD&trade;

DX-CAD&trade; is parametric CAD on the OpenCASCADE kernel under its EULA, free for
30 days from first start, then a licence (opening, viewing and exporting stay
free), with an open-source SDK under Apache 2.0. Every model is
a Python script; every operation is reachable from the command line and from an
agent; the window is a viewer and a sketchpad on top of that, not the other way
round. What the project is for, what it will not do and where it is going are
in DX-CAD's README.md,
which is its page on PyPI too, and how to install it is in
[install.md](install.md).

These are the pages.

| Page | What it holds |
| --- | --- |
| [index.md](index.md) | This page: what DX-CAD is, and where every other page is. |
| [install.md](install.md) | Installing DX-CAD: from PyPI, and the Windows, macOS and Linux builds, with how each unsigned build opens the first time. |
| [cli.md](cli.md) | Every `dxcad` subcommand: what it takes, what it writes, every option it has, what it exits with, and one command to paste. |
| [kernel.md](kernel.md) | The model language: every name a model.py has in scope, with its signature, and three worked models. |
| [gui.md](gui.md) | The window: how to open it, every menu and action it has with its shortcut, the model pane and the run key. |
| [agents.md](agents.md) | `dxcad serve`, the MCP server: how to point Claude Code and Claude Desktop at it, where it may write, and every tool it offers. |
| [plugins.md](plugins.md) | Plugins: how a package adds model names, `dxcad` subcommands, MCP tools and window actions, with a minimal example. |
| [drawing.md](drawing.md) | Drawings and model.py: the drawing functions a plugin adds to the model language, and the drawing a plugin's tool is handed. |
| [sheetmetal.md](sheetmetal.md) | Sheet metal: how a sheet part is made, flanged and unfolded to a flat pattern, from a model.py, the command line, the window and the agent door, with a worked tray. |
| [gallery.md](gallery.md) | The gallery: every example rendered, with its script, and the sheet parts' flat patterns. |
| [contributing.md](contributing.md) | Contributing: where the rules are, and a first contribution walked through, a gallery part from starter to signed-off commit. |
| [admin.md](admin.md) | AI policy for IT departments: the allowed providers, the agent door, what may be sent, and AI features off, with sample registry and policy files. |
| [limitations.md](limitations.md) | Known limitations: what DX-CAD cannot do or does unreliably on OCCT, why, and what to do instead, with every robustness case's outcome. |
| [settings.md](settings.md) | Settings and their scope: everything DX-CAD keeps, and whether it is the document's, the session's or yours. |
| [examples/README.md](examples/README.md) | The example parts, a model.py each, with what every one of them shows and how to run it. |
| [examples/bracket.md](examples/bracket.md) | The worked example: a bracket with four holes, made by an agent from one sentence. |
| [examples/dimensions.md](examples/dimensions.md) | Where each fastener figure in the examples comes from. |
| [tutorials/first-part.md](tutorials/first-part.md) | Tutorial: your first part, a plate drilled and exported, from a model.py. |
| [tutorials/sheet-metal.md](tutorials/sheet-metal.md) | Tutorial: sheet metal in 10 minutes, a tray with flanges, its flat and the DXF a laser cuts. |
| [tutorials/corner-post.md](tutorials/corner-post.md) | Tutorial: corner post in the window, a door's corner post bent with Base Flange and Flange alone, flanges on flanges' edges and its flat. |
| [tutorials/assemblies.md](tutorials/assemblies.md) | Tutorial: assemblies with mates, a bolt in a plate, then that pair used twice as a sub-assembly. |
| [tutorials/drawing.md](tutorials/drawing.md) | Tutorial: drawing a part on an A3 sheet with its parts list, exported to PDF and DXF. |
| [tutorials/claude-desktop.md](tutorials/claude-desktop.md) | Tutorial: DX-CAD with Claude Desktop, connected to the open window, and three prompts. |

Everything here is markdown in the repository, so it reads on GitHub as it
stands. The test suite reads it too: every link on every page names a file that
is there, and every page of the site is reachable from this one.
