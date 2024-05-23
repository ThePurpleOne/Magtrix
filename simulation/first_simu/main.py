import biot_savart as bs

bs.write_target_volume("coil.txt", "coil", (30, 15, 15), (-5, -0.5, -2.5), 1, 1)
# generates a target volume from the coil stored at coil.txt
# uses a 30 x 15 x 15 bounding box, starting at (-5, -0.5, -2.5)
# uses 1 cm resolution

bs.plot_coil("coil.txt")
# plots the coil stored at coil.txt

fields, positions = bs.read_target_volume("coil")
# reads the volume we created

bs.plot_fields(fields, positions, which_plane='z', level=5, num_contours=50)
# plots the fields we just produced
# plotting along the plane x = 5, with 50 contours