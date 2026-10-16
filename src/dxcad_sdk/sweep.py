# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""dxcad-sdk sweep NAME: DX-CAD's command sweep, run on an installed add-on's commands.

DX-CAD item 786. The sweep opens each of the add-on's commands in DX-CAD's
own window, offscreen, from four states (nothing open, a part picked, a
closed sketch in hand, a sheet part picked), and checks every dialog it opens
on a 1366 x 768 screen at 100, 125 and 150 percent (it fits, its OK and
Cancel are shown, OK is enabled with the defaults, Enter accepts, Esc
cancels), then accepts it with its defaults and checks that every part the
command adds is a valid solid that the model, run again, builds. Each
failure is one line, "KEY: CHECK: what was found".

The sweep is DX-CAD's, `python -m dxcad.gui.sweep --plugin NAME`, run in a
process of its own with settings, recovery files and the window channel in
a folder of its own, so DX-CAD must be installed in the same Python as the
add-on; this module imports none of it. `--known FILE` names failures the
add-on knows of, one "KEY: CHECK" a line: those are passed over, and a known
one that now passes is a failure, so the list only shrinks.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

#: The module that runs DX-CAD's sweep.
SWEEP_MODULE = "dxcad.gui.sweep"

#: What is said, and the exit status, when DX-CAD is not in this Python.
NO_DXCAD = (
    "dxcad-sdk sweep: DX-CAD is not installed in this Python ({python}); the sweep runs "
    "DX-CAD's own window, so install DX-CAD beside the add-on"
)
NO_DXCAD_STATUS = 2


def command(name: str, known: Path | None = None, python: str = sys.executable) -> list[str]:
    """The command that sweeps plugin `name`'s commands."""
    line = [python, "-m", SWEEP_MODULE, "--plugin", name]
    if known is not None:
        line += ["--known", str(known)]
    return line


def run(name: str, known: Path | None = None) -> int:
    """Sweep plugin `name`'s commands, its lines printed as they come; the sweep's exit status."""
    if importlib.util.find_spec("dxcad") is None:
        print(NO_DXCAD.format(python=sys.executable))
        return NO_DXCAD_STATUS
    sys.stdout.flush()
    return subprocess.run(command(name, known), check=False).returncode
