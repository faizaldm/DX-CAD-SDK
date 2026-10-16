# post_ends.py
spec = SheetSpec(1.5, 1.5, 0.44)
post = base_flange([(3, 3), (127, 3), (127, 197), (3, 197)], spec, Plane.XZ)
post = flange(post, 3, 120, 90, "down", return_length=23.5, length_from="outside")
post = flange(post, 1, 20, 90, "down", return_length=10, length_from="outside")
for edge in (0, 2):
    post = flange(post, edge, 20, 90, "down", return_length=10,
                  length_from="outside", corner_treatment="square")
post = flange(post, (3, "free"), 10, 90, "down", length_from="outside")
for end in ("start", "end"):
    post = flange(post, (3, end), 26.5, 90, "up", return_length=10,
                  length_from="outside", corner_treatment="mitre")

part("post", post, color="galvanised")
