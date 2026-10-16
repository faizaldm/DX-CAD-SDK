# post_base.py
spec = SheetSpec(1.5, 1.5, 0.44)
post = base_flange([(3, 3), (127, 3), (127, 197), (3, 197)], spec, Plane.XZ)

part("post", post, color="galvanised")
