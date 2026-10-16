# tray.py
LENGTH = 160.0
WIDTH = 100.0
HEIGHT = 30.0
HOLE = 10.0

spec = SheetSpec.from_gauge("mild steel", 1.5)
outline = [(0, 0), (LENGTH, 0), (LENGTH, WIDTH), (0, WIDTH)]
tray = base_flange(outline, spec, holes=[(LENGTH / 2, WIDTH / 2, HOLE)])
for edge in range(4):
    tray = flange(tray, edge, HEIGHT)

part("tray", tray, color="galvanised")
