# plate_holes.py
LENGTH = 80.0
WIDTH = 50.0
THICK = 6.0
HOLE = 6.5
INSET = 10.0

plate = make_box(LENGTH, WIDTH, THICK)
for x in (INSET, LENGTH - INSET):
    for y in (INSET, WIDTH - INSET):
        plate = cut(plate, make_cylinder(HOLE / 2, THICK, (x, y, 0)))
plate = chamfer_all(plate, 0.5)
part("plate", plate, color="steel")
