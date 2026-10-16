# angle.py
LENGTH = 60.0
WIDTH = 40.0
HEIGHT = 30.0
THICK = 4.0
HOLE = 5.5

angle = fuse(make_box(LENGTH, WIDTH, THICK), make_box(LENGTH, THICK, HEIGHT))
for x in (LENGTH / 4, 3 * LENGTH / 4):
    hole = make_cylinder(HOLE / 2, THICK, (x, (WIDTH + THICK) / 2, 0))
    angle = cut(angle, hole)
part("angle", angle, color="galvanised")

for x in (LENGTH / 4, 3 * LENGTH / 4):
    part(f"foot_{int(x)}", make_cylinder(6, 3, (x, (WIDTH + THICK) / 2, -3)), color="black")
