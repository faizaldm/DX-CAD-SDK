<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Designmatix Ltd -->
# The .dxcprt, .dxcasm and .dxcdrg file formats

This is file format 2, which records each file's kind: a part, an assembly or
a drawing, saved as .dxcprt, .dxcasm and .dxcdrg. Every file written from 0.1
on records its format version under `"format_version"`; a file without one is
format 1. A format 1 file is given its kind as it opens:
an older .dxcad with one part is a part (an assembly if its model.py calls
`use()`), one with more is an assembly, and
an older .dxcaddrg is a drawing; DX-CAD saves it in its new type beside
the old file. A DX-CAD that meets a newer format than it reads refuses the file
before reading any of it, naming both versions. An older format is brought up
to date on opening, one version at a time, so a format 1 file opens in every
later release.

## .dxcprt and .dxcasm: a part and an assembly

A part file (.dxcprt) or an assembly file (.dxcasm) is a zip archive; the two
are one format, told apart by `"kind"` below. A person can open it with any zip tool and take a
part out: each part is a member of its own.

| Member | What it holds |
| --- | --- |
| `manifest.json` | the index, below |
| `0000.brep`, `0001.brep`, ... | one part each, in OCCT's BREP format, numbered in document order |
| `model.py` | the script that built the parts, UTF-8, its bytes as typed; absent when there is none |

Members are numbered, never named after their parts, so a part's name can
never become a path.

### manifest.json

A JSON object:

| Key | Type | Meaning |
| --- | --- | --- |
| `"format_version"` | integer | the file format, 2 |
| `"kind"` | text | `"part"` or `"assembly"`; absent in format 1 |
| `"schema_version"` | integer | the archive's layout: 1 (STEP members, `.step`), 2 (BREP members), 3 (BREP members and an optional model.py); DX-CAD 0.1 writes 3 |
| `"dxcad_version"` | text | the DX-CAD that wrote the file, such as "0.1.0" |
| `"entries"` | list | each part, in document order, as `{"name": NAME, "file": MEMBER}` |
| `"script"` | text | the model.py member's name, `"model.py"`; absent when there is no script |
| `"plugins"` | object | each plugin's own section, by plugin name; absent when there is none |

A part's name is unique within the file. The BREP members are the parts as
they were when the file was saved; the script, when there is one, is how they
were made, and running it again builds them afresh.

### A plugin's section

Under `"plugins"`, each plugin's section is an object:

| Key | Type | Meaning |
| --- | --- | --- |
| `"version"` | text | the plugin's version when the file was saved |
| `"parts"` | list of text | the names of the parts the plugin made |
| `"data"` | object | whatever the plugin keeps; DX-CAD stores and returns it untouched |

A file whose plugin is not installed still opens: its parts show as their
stored solids, marked "made with NAME, not installed", and running its script
is refused with the same words.

## .dxcdrg: a drawing

A .dxcdrg is a drawing of one part or assembly. It holds no geometry: whenever
it is drawn the model is read again, so the drawing follows the model. It is
UTF-8 JSON, one object:

| Key | Type | Meaning |
| --- | --- | --- |
| `"format"` | text | always `"dxcaddrg"` |
| `"format_version"` | integer | the file format, 2 (a drawing saved before format versions kept it under `"version"`) |
| `"kind"` | text | always `"drawing"`; absent in format 1 |
| `"model"` | text | the model's path, relative to the drawing where it can be, with forward slashes |
| `"sheet"` | text | the sheet: A4, A3, A2, A1, ISO-A4-portrait, ISO-A4, ISO-A3, ISO-A2, ISO-A1, ISO-A0, ANSI-A, ANSI-B, ANSI-C or ANSI-D; A3 when absent |
| `"scale"` | [drawn, true] or null | the scale chosen, such as [1, 2]; null for the standard scale that fits |
| `"views"` | object | each view moved from where the sheet puts it (front, top, right or iso) as [dx, dy] in the sheet's millimetres |
| `"dimensions"` | true or false | whether dimensions are shown; true when absent |
| `"parts_list"` | true or false | whether the parts list is shown; true when absent |
| `"fields"` | object | the title block's fields, text by key: company_name, drawn_by, checked_by, material, finish, tolerance, drawing_no, rev_number |
| `"hidden_off"` | list of text | the views whose hidden lines are not shown |
| `"font"` | text or null | the font the sheet is lettered in; null for the bundled font |
| `"text_height"` | number or null | the text height in mm (2.5, 3.5 or 5); null for the sheet's own |
| `"precision"` | number | the precision the overall sizes are held to, in mm (1, 0.1 or 0.01), their trailing zeros kept; absent for the sheet's own, from its scale and the general tolerance |
| `"removed"` | list of text | the standard views taken off the sheet (DX-CAD item 790), which it does not draw; absent when none is |
| `"plugins"` | object | each plugin's section, by name: its `"views"` (each `{"kind", "at", "data"}`), its `"annotations"` (each `{"kind", "view", "ref", "data"}`) and the `"output"` it last drew (`{"strokes", "texts", "images"}` in the sheet's millimetres, each image a PNG as base64 and the box it fills), shown in its place, with a notice, where the plugin is not installed or is locked; empty when absent |

A drawing whose model is not there is reported by the model's path.

## latest.json: what DX-CAD reads of a release

Help > Check for Updates, and the check at start, read latest.json from the
SDK's site, written by the core's export. DX-CAD keeps what it reads of buying
in the user's settings, so the last answer holds offline. Every key but the
first four may be absent; one that is not of its kind is passed over.

| Key | Kind | Meaning |
|---|---|---|
| `"version"` | text | the newest release, such as 0.1.2 |
| `"date"` | text | the day it was released, as an ISO date (2026-10-25) |
| `"note"` | text | a line saying what it is |
| `"url"` | text | where it is downloaded |
| `"buy_url"` | text | where a licence is bought; DX-CAD's own site when absent |
| `"addons"` | object | the add-ons on sale, by name |
| `"licences_from"` | text | the day licences go on sale, as an ISO date (DX-CAD item 919): until that day, UK time, Help > Licence's Activate, Send code and Sign in contact nothing and say from which day licences are available, and no buy link is shown; 2026-11-01 when absent |
| `"trial_until"` | text | an ISO date (DX-CAD item 919): no trial locks before 23:59 UK time on it, so it can only put a trial's end later; it changes nothing for a licensed install, or once the day has passed |
