from magneticalc import API
import numpy as np


side_width = 8
spacing = 0.2
line_width = 0.3
out_pad_displacement = 0.7  # How much is the pad displaced
in_pad_displacement = 0.4


def create_coil_segments() -> list:
    """
    This will create the actual segments of the coil.
    This uses kmt.Line to create the segments of the coil.
    returns: List of 3D points representing the coil.
    """

    # Get the number of turns we can execute considering
    # the spacing and the line width
    number_of_turns = int(side_width / (line_width + spacing)) - 1

    points = []

    # Start point (3D point format with z = 0)
    points.append((side_width + out_pad_displacement, -side_width, 0))

    for i in range(number_of_turns):
        r = side_width - i * (line_width + spacing)
        next_r = r - (line_width + spacing)

        # Penultimate segment, cut it short to reach the y = 0
        # If it's the last segment, we need to connect it to the middle pad
        if i == (number_of_turns - 1):
            turn_points = [
                (-r, -r, 0),
                (-r, r, 0),
                (r, r, 0),
                (r, 0, 0),
                (0, 0, 0),
            ]
        else:
            turn_points = [
                (-r, -r, 0),
                (-r, r, 0),
                (r, r, 0),
                (r, -next_r, 0),
            ]

        points.extend(turn_points)

    return points




wire = create_coil_segments()
print(wire)

API.export_wire("square_wire.txt", wire)