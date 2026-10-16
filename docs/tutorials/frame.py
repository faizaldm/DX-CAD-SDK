# frame.py
pair = use("bolt_plate.dxcasm", as_group=True)

rail = make_box(200, 60, 10)
for x in (30, 150):
    rail = cut(rail, make_cylinder(3, 10, (x, 30, 0)))
part("rail", rail, color="navy")
place("left", pair, at=(10, 10, 10))
place("right", pair, at=(130, 10, 10))
