# plate.py
LENGTH = 80.0
WIDTH = 50.0
THICK = 6.0

plate = make_box(LENGTH, WIDTH, THICK)
part("plate", plate, color="steel")
