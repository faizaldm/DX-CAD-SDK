# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""Keep every test of this plugin out of the user's own DX-CAD folders.

DX-CAD writes its log, its settings, its autosave recovery and its add-ons'
state outside any document; a plugin's tests call the installed DX-CAD, so
without this they would write into the user's own folders. DXCAD_HOME moves
all of them to the folder it names: here, a folder of each test's own.
"""

import os
import tempfile

import pytest

# Set while this file is imported too, so nothing that runs before the first
# test, and no process a test starts, meets the user's folders.
os.environ["DXCAD_HOME"] = tempfile.mkdtemp(prefix="dxcad-plugin-tests-")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def private_home(monkeypatch, tmp_path_factory):
    """Every test's DX-CAD files under a folder of its own."""
    folder = tmp_path_factory.mktemp("dxcad-home")
    monkeypatch.setenv("DXCAD_HOME", str(folder))
    return folder
