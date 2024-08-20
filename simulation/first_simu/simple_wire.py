from magneticalc import API
import numpy as np


spacing = 0.2 # mm
line_width = 0.3 # mm
length = 0.8 # mm


# Create a simple straight wire
wire = [
	(0, 0, 0),
	(0, length, 0),
]

API.export_wire("simple_wire.txt", wire)