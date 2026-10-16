# desk_plate.py
plate = make_box(50, 30, 5)
for x in (5, 45):
    for y in (5, 25):
        plate = cut(plate, make_cylinder(2, 5, (x, y, 0)))
plate = chamfer_all(plate, 0.5)
part("plate", plate)
