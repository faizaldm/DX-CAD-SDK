# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""The DX-CAD SDK: interfaces, stubs, docs and examples for building on DX-CAD.

dxcad_sdk.plugin is the plugin API, as protocols and constants; the
dxcad-stubs package beside this one types every function a model.py starts
with; `dxcad-sdk check PATH` checks an add-on's declarations. The SDK holds
no part of DX-CAD and is licensed apart from it (see NOTICE).
"""

from dxcad_sdk.plugin import (
    API_VERSION,
    ENTITLEMENT_GROUP,
    ENTRY_POINT_GROUP,
    Action,
    AnnotationKind,
    Command,
    Document,
    EntitlementProvider,
    Pick,
    Registry,
    SheetKind,
    SheetTool,
    Tool,
    ViewKind,
    Window,
)

__version__ = "0.1.1"

__all__ = [
    "API_VERSION",
    "ENTITLEMENT_GROUP",
    "ENTRY_POINT_GROUP",
    "Action",
    "AnnotationKind",
    "Command",
    "Document",
    "EntitlementProvider",
    "Pick",
    "Registry",
    "SheetKind",
    "SheetTool",
    "Tool",
    "ViewKind",
    "Window",
    "__version__",
]
