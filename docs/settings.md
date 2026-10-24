# Settings and their scope

Everything DX-CAD&trade; keeps has one of three scopes: it is the document's, the session's or yours. Nothing that hides or moves part of the model is on unseen: while Section View is on, parts are hidden or the view is exploded, a banner over the 3D view says so, with a button that turns it off, and a section's cutting plane is drawn faintly.

This page is written from `dxcad.scopes.INVENTORY`, which the test suite holds to the window: a tick, a stored key or a drawing's field it does not name fails the build.

## The document's

These belong to the file in front. They stay with it while you work in other tabs, a new file and an example start with each at its default, and those kept in the file come back when it is opened.

| Setting | Default | Kept in | Found as |
| --- | --- | --- | --- |
| Where the model is looked at from | isometric, fitted to the parts | the file | `target`, `distance`, `azimuth`, `elevation`, `front`, `back`, `left`, `right`, `top`, `bottom`, `iso` |
| Hidden parts | every part shown | the file | `hidden` |
| Section View: its plane, how far it is moved and the side shown | off | the file | `section_view`, `section` |
| Explode | assembled | the file | `explode` |
| How parts are drawn: shaded with edges, shaded, wireframe or translucent | shaded with edges | the file | `display_shaded_edges`, `display_shaded`, `display_wireframe`, `display_translucent`, `mode` |
| What an add-on keeps for the document | nothing | the file | `settings` |
| Run on Change | off | the open document | `run_on_change` |
| No Time Limit | off | the open document | `no_time_limit` |
| Show Overhangs | off | the open document | `show_overhangs` |
| Flat Pattern of the picked part | off | the open document | `flat_part` |
| A drawing's sheet size | ISO A3 | the file | `sheet` |
| A drawing's scale, and a view's own | the largest that fits | the file | `scale`, `view_scales` |
| Where each view of a drawing is, and the views taken off | laid out in first-angle | the file | `views`, `removed`, `unlocked` |
| A drawing's dimensions and their decimals | shown, as the sheet's standard has them | the file | `dimensions`, `precision` |
| A drawing's parts list and its columns | shown, with the columns chosen last | the file | `parts_list`, `columns` |
| A drawing's title block | the fields typed last | the file | `fields`, `labels` |
| Hidden lines of each view of a drawing | off in a new view | the file | `hidden_off` |
| A drawing's lettering | the sheet's own | the file | `font`, `text_height` |
| Small parts left out of a view of a drawing | none left out | the file | `leave_out` |
| The line type Line and Polyline draw with on a drawing | thin | the file | `line_style` |
| A drawing's model, its sheets and what add-ons keep in it | one sheet of the model | the file | `model`, `sheets`, `part`, `name`, `plugins`, `preview`, `parent` |

## The session's

These last until DX-CAD closes. The next start has each at its default.

| Setting | Default | Found as |
| --- | --- | --- |
| The script pane shown | shown when a file has a model | `script_pane` |
| The output pane shown | hidden | `output_pane` |
| The feature tree shown | hidden | `feature_tree_pane` |
| The Assistant's panel shown | hidden | `assistant` |
| Continuous Orbit and Turntable | off | `continuous_orbit`, `turntable` |
| The sketch tool in hand, Trim and Break | Line, at the start of each sketch | `tool_line`, `tool_rectangle`, `tool_circle`, `tool_arc`, `tool_centre_arc`, `tool_polygon`, `tool_slot`, `tool_ellipse`, `tool_spline`, `trim_sketch`, `break_sketch` |
| Measure on | off | `measure` |
| Ortho on a drawing | off | `drawing_ortho` |
| The number of sides Polygon offers | 6 | - |
| The folder a file box opens in | the file's own | - |

## Yours

These are kept for you across starts, whatever file is open. Most are changed in File > Settings or by the menu entry named.

| Setting | Default | Found as |
| --- | --- | --- |
| Theme | light | `theme_light`, `theme_dark`, `view/theme` |
| Planes shown | shown | `show_planes`, `view/show_planes` |
| Turn the view after a run | on | `turn_after_run`, `view/turn_after_run` |
| The Parts and History panels shown | shown | `parts_pane`, `history_pane`, `view/parts_dock`, `view/history_dock` |
| Each toolbar shown | shown | `view/toolbar_{name}` |
| Documents as tabs, tiled or cascaded | tabs | `tabbed_windows`, `tile_windows`, `cascade_windows`, `window/arrangement` |
| Mode, and the layout it was last given | the full window | `window/mode`, `window/layout_version` |
| Mouse controls | DX-CAD's own, asked once | `controls/preset`, `controls/asked` |
| Stop spinning when DX-CAD loses focus | on | `view/stop_spin_on_focus_loss` |
| The formed part shown faintly behind a flat pattern | on | `view/flat_ghost` |
| The edge of the blank a flat pattern's bend lines are measured from | left | `view/flat_datum` |
| Keep unsaved tabs every | 5 minutes | `recovery/minutes` |
| Default material | none | `parts/default_material` |
| Ask to lay a drawing out for speed above | 100 parts | `drawing/large_assembly` |
| The columns and title block a new drawing starts with | those used last | `drawing/columns`, `title_block` |
| Check for updates at start | on | `updates/at_start` |
| Recent files | none | `recent_files` |
| What has been shown once: the first run, and what is new in a version | not yet shown | `first_run/done`, `whats_new/version` |
| The slicer Send to Slicer starts | asked for | `slicer/program` |
| The sheet a new base flange is made of | 2 mm, bend radius 2 mm, K 0.44 | `sheet/thickness`, `sheet/bend_radius`, `sheet/k_factor` |
| Flat pattern profiles | none | `flat/profiles` |
| The Assistant: on or off, its provider, model, address and limits, and its panel's place | off | `assistant/enabled`, `assistant/model`, `assistant/reply_limit`, `assistant/context_tokens`, `assistant/provider`, `assistant/endpoint`, `assistant/models/{provider}`, `assistant/addresses/{provider}`, `assistant/noted/{provider}`, `assistant/warn_at`, `assistant/area`, `assistant/floating`, `assistant/height` |
| Add-ons bought, and where they are bought | none | `paid/addons`, `paid/assistant_endpoint`, `paid/buy_url` |
| The licence: this install, its key and what it was last told | a trial | `licence/install_id`, `licence/token`, `licence/key`, `licence/noticed`, `licence/trial_started/{install}`, `licence/latest_seen`, `licence/latest_pending`, `licence/clock_gap` |
| What an add-on keeps for you | the add-on's own | `plugins/{name}` |

## Add-ons

An add-on declares each setting it keeps with its scope, `registry.setting(name, title, scope, default)`, the scope one of `"document"`, `"session"` and `"preference"`, and reads and writes it with `window.plugin_setting(plugin, name)` and `window.set_plugin_setting(plugin, name, value)`. DX-CAD keeps it where its scope says: in the file, in the window until DX-CAD closes, or in your settings.
