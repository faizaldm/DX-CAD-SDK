# The two-minute demo

What DX-CAD is, shown rather than explained, in under two minutes: a part that
is a script, one number changed, the part described, exported, opened in the
window, and then made again by an agent through the same kernel.

The recording itself wants a screen and a person, and is not something the
test suite can make. What the suite does is run the commands, in this order,
in one empty directory, at every commit: a demo whose commands have never been
run in order is how a recording goes wrong on the seventh take.

Every beat below carries the seconds it takes, one line of what is said over
it, and the commands exactly as they are typed. They come to 120 seconds.

### 1. A model is a script (10 seconds)

"This is a CAD part. It is also a Python file: nine numbers and a dozen
lines."

```
dxcad examples bracket
```

Show bracket.py on screen, the constants at the top.

### 2. Run it (15 seconds)

"Running it builds the part. The script goes inside the file it built, so the
part can always say where it came from."

```
dxcad run bracket.py --output bracket.dxcprt
```

### 3. Ask what it is (15 seconds)

"Nothing is guessed at: volume, bounds, faces by kind, and the four holes with
their diameter and depth."

```
dxcad describe bracket.dxcprt
```

### 4. Change one number (30 seconds)

"Make it a hundred long. That is the whole of the parametric model: change a
number, run it again, and the holes move with it."

Edit bracket.py: `LENGTH = 80.0` becomes `LENGTH = 100.0`

```
dxcad run bracket.py --output bracket.dxcprt --force
dxcad describe bracket.dxcprt
```

### 5. Hand it to anyone else (10 seconds)

"STEP out, for whatever else the shop runs."

```
dxcad export bracket.dxcprt bracket.step
```

### 6. Look at it (20 seconds)

"And there it is, with the script beside it. Change the number in the pane,
press F5, and the part follows."

```
dxcad gui bracket.dxcprt
```

Not run by the test: the window opens and waits for a person, and whether it
draws the part correctly is a manual check. What the window holds is in
[gui.md](gui.md).

### 7. Or say it in a sentence (20 seconds)

"Same kernel, no window: an agent makes the part from a sentence and saves it
where you asked."

```
claude mcp add dxcad -- dxcad serve
```

Then, to the agent: *Make me a mounting bracket 100 long: a base 30 deep and
an upright 46 high along its back edge, both 6 thick, with four 5 mm holes in
a row through the base. Then save it.*

Not run by the test: it wants an MCP client and a model of somebody else's,
neither of which this suite has. The same conversation, every request and
every answer, is in [examples/bracket.md](examples/bracket.md), and the suite
does play that one down the server's own pipe.
