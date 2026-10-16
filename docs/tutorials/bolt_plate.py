# bolt_plate.py
THICK = 5.0
RADIUS = 3.0

plate = cut(make_box(60, 40, THICK), make_cylinder(RADIUS, THICK, (20, 20, 0)))
part("plate", plate, color="steel")

bolt = fuse(make_cylinder(RADIUS, 20), make_cylinder(5, 4, (0, 0, 20)))
part("bolt", translate(bolt, (100, 50, 30)), color="hardware")
mate("bolt", "cylinder 1", "plate", "hole 1", "concentric")
mate("bolt", "<Z 2", "plate", ">Z", "coincident")
