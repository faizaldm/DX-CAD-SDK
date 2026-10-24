# Example parts

Every part here is a model.py: a short Python script with its numbers at the
top. Every name the kernel and the sketch API have is already in scope, so a
model imports nothing. To build one into a project, and to look at it:

```
dxcad run bracket.py --output bracket.dxcprt
dxcad describe bracket.dxcprt
dxcad gui bracket.py
```

Change a number and run it again: that is the whole of DX-CAD&trade;'s parametric
model. The test suite runs every model on this page, checks each part it
builds against arithmetic, and builds it again with one number changed, so
what is written here is what the script does.

A sketch is drawn on a plane. `Plane.XY`, `Plane.XZ` and `Plane.YZ` are the
three standard ones, `Plane.XY.offset(z)` is XY lifted by `z`, which is what
`engine_inline4.py` draws its bolt heads on, and `Plane.from_face(face)` is
the plane of a face of a part already built.

| Model | What it is |
| --- | --- |
| [bolt_mate.py](bolt_mate.py) | A bolt placed in a plate's hole by two mates, as docs/kernel.md shows it. |
| [bracket.py](bracket.py) | A mounting bracket with four holes: the worked example of docs/examples/bracket.md. |
| [channel.py](channel.py) | A lipped channel, its width, depth and lips dimensioned to the outside. |
| [clip.py](clip.py) | A cable clip, drawn with arcs. |
| [corner_post.py](corner_post.py) | A door corner post bent from one 1.5 mm sheet, with flanges on its flanges' edges. |
| [door.py](door.py) | A door hung on one hinge sub-assembly used twice, from door-hinge.dxcasm. |
| [drawn_bracket.py](drawn_bracket.py) | An angle bracket with its drawing, drawn_bracket.dxcdrg, on an ISO A3 sheet. |
| [enclosure.py](enclosure.py) | A box and its lid, two parts from one model. |
| [engine_inline4.py](engine_inline4.py) | Inline-four DOHC petrol engine, cut away. |
| [flange.py](flange.py) | A pipe flange with a bolt circle. |
| [funnel.py](funnel.py) | A funnel, a thin wall turned about its axis. |
| [gearbox.py](gearbox.py) | A two-stage helical speed reducer, its cover cut away to show the gear train. |
| [handle.py](handle.py) | A bent handle, a round bar swept along a path. |
| [knob.py](knob.py) | A scalloped knob with a pocket for a captive nut. |
| [mated_enclosure.py](mated_enclosure.py) | A round enclosure whose lid is placed on its base by two mates. |
| [mitred_door.py](mitred_door.py) | A 1000 x 800 cabinet door bent from 2 mm steel, its return lips mitred at the corners. |
| [race_car_frame.py](race_car_frame.py) | A Formula Student race car: tubular spaceframe chassis and running gear. |
| [rack.py](rack.py) | A welded rack frame on castors, from plain parts. |
| [relieved_tray.py](relieved_tray.py) | A sheet metal tray with two relieved flanges and two holes in its base. |
| [robot_arm.py](robot_arm.py) | A six-axis industrial robot arm in a working pose, with a parallel gripper. |
| [sheet_door.py](sheet_door.py) | A cabinet door bent from 1.5 mm mild steel, with flanges and return lips. |
| [steel_structure.py](steel_structure.py) | A two-level industrial steel platform, 3 x 2 bays. |
| [tray.py](tray.py) | A sheet metal tray, a flange bent up on each edge of its base. |

Seven of them show what v0.1 adds: sheet metal with relief and holes
(relieved_tray.py) and dimensioned to the outside (channel.py), parts placed
by mates (mated_enclosure.py, bolt_mate.py), a sub-assembly used twice
(door.py), raised text (the nameplate of gearbox.py) and a drawing document
(drawn_bracket.py). Two keep a file beside them: door.py uses
door-hinge.dxcasm, and drawn_bracket.dxcdrg is the bracket's drawing.
`dxcad examples door` copies the file along with the model.

Five are whole machines of some two hundred to four hundred parts each:
gearbox.py, engine_inline4.py, robot_arm.py, race_car_frame.py and
steel_structure.py. Each opens drawn light, so that it builds in a few
seconds, and its docstring names the numbers that draw it in full: the
gear teeth's involutes, the cam lobes, the bores of the suspension tubes,
the bolts on every end plate.

Some of the numbers in these models are not chosen but looked up: a clearance
hole, a tapping drill, the seat a screw head sits in.
[dimensions.md](dimensions.md) says where each of those comes from.

The bracket is also the worked example for agents: [bracket.md](bracket.md)
tells the story of an agent making it through `dxcad serve`, and
[bracket.jsonl](bracket.jsonl) is that conversation, line for line.
