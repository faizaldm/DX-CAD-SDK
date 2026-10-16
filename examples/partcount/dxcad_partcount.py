# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Designmatix Ltd
"""An example plugin that gives agents a tool: part_count, which reads the document.

`dxcad serve` publishes it beside DX-CAD's own tools; an agent calls it with
no inputs, or with `prefix` to count only the parts whose names start so.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "prefix": {"type": "string", "description": "count only names starting with this"},
    },
    "required": [],
}


def part_count(document, arguments):
    """How many parts the document holds, and their names."""
    prefix = str(arguments.get("prefix", ""))
    names = [name for name, _ in document if name.startswith(prefix)]
    return {"count": len(names), "names": names}


def register(registry):
    registry.require(1)
    registry.tool(
        "part_count",
        "How many parts the document holds, and their names; prefix counts only names "
        "that start with it.",
        SCHEMA,
        part_count,
        reads=True,
    )
