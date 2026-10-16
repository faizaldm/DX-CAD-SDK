# A bracket with four holes, from a sentence

This is what an agent does with `dxcad serve` when it is given one sentence:

> Make me a mounting bracket 80 long: a base 30 deep and an upright 46 high
> along its back edge, both 6 thick, with four 5 mm holes in a row through
> the base. Then make it 100 long, and save it.

Three files tell it. This page is the story; [bracket.jsonl](bracket.jsonl)
is the conversation itself, every request a client sends, one a line, from
`initialize` to `project_save`; and [bracket.py](bracket.py) is the same part
as a model. The test suite plays both, so what is written here is what the
server does. How to point Claude Code or Claude Desktop at the server is in
[../agents.md](../agents.md).

## The section, extruded

The bracket is an L in section, so the agent draws the L on the YZ plane,
base along Y and upright along Z, and extrudes it 80 along X:

```json
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "sketch_extrude", "arguments": {"name": "bracket", "plane": "YZ", "profile": [{"op": "move_to", "point": [0, 0]}, {"op": "line_to", "point": [30, 0]}, {"op": "line_to", "point": [30, 46]}, {"op": "line_to", "point": [24, 46]}, {"op": "line_to", "point": [24, 6]}, {"op": "line_to", "point": [0, 6]}, {"op": "close"}], "height": 80}}}
```

The answer is the part's facts, which is the only look at it the agent gets:
one valid solid of volume 33600.000, which is the L's area, 30 x 6 + 6 x 40 =
420, times 80; size 80 x 30 x 46; eight flat faces; no holes yet.

## Four holes in one call

The agent does not work out four centres. It makes one drill, a cylinder of
radius 2.5 through the base at the first hole, 10 from the end and half way
across the 24 of base that the upright leaves clear:

```json
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "make_cylinder", "arguments": {"name": "drill", "radius": 2.5, "height": 6, "origin": [10, 12, 0]}}}
```

and patterns it, four in a row 20 apart, cut from the bracket:

```json
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "linear_pattern", "arguments": {"name": "drill", "step": [20, 0, 0], "count": 4, "cut_from": "bracket"}}}
```

The drill is taken out of the document afterwards, as a cutting tool should
be, and the whole call is one undo. The answer is the bracket again: volume
33128.761, which is 33600 less four cylinders of pi x 2.5 x 2.5 x 6, and
twelve faces, eight flat and four cylindrical.

## Counting them

An agent that was asked for four holes has to be able to count them:

```json
{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "describe", "arguments": {"name": "bracket"}}}
```

`describe` answers, among the rest, `"holes"`: four of them, each of diameter
5 and depth 6, along Z, through, with centres at x = 10, 30, 50 and 70, y =
12. That is the sentence, checked.

## The same part as a model

Every DX-CAD model is a script. The agent writes the part down as one,
[bracket.py](bracket.py), whose numbers are names at the top of the file, and
runs it with `run_model`. That tool and `model_set` run Python, so the server
must have been started with `--allow-run`; without it both are refused. The server answers `"changed": []`: the model
builds, to the last face, the bracket the tools had already made. The
document now carries the model, so the project saved from it is parametric.

## Longer, without writing it again

`model_values` lists the numbers the model is made of, LENGTH, DEPTH, HEIGHT,
THICKNESS, HOLES, HOLE_DIAMETER and INSET. To make the bracket 100 long the
agent changes one of them and the server runs the model again:

```json
{"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "model_set", "arguments": {"values": {"LENGTH": 100}}}}
```

The model spaces its holes from the length, so they move with it: the
bracket is now 100 x 30 x 46 with a volume of 41528.761, which is 420 x 100
less the same four cylinders, and a last `describe` still counts four holes
of diameter 5, now at x = 10, 36.667, 63.333 and 90. One `undo` would put
back the 80 bracket and the old text together.

## Saved

```json
{"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "project_save", "arguments": {"path": "bracket.dxcprt"}}}
```

`bracket.dxcprt` lands in the server's working directory. It opens in the
window with `dxcad gui bracket.dxcprt`, model and all, and `dxcad describe
bracket.dxcprt` says in words what the agent was told in JSON.

## Trying it

With nothing but a shell, from this directory:

```
dxcad serve --allow-run < bracket.jsonl
```

Without `--allow-run` the `run_model` and `model_set` requests are refused.

prints one reply a line and leaves `bracket.dxcprt` behind.
