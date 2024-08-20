from magneticalc import API
import numpy as np
import matplotlib.pyplot as plt

spacing = 0.2 # mm
line_width = 0.3 # mm
diameter = 8 # mm
radius = diameter / 2

num_turns = radius / spacing


# Create a round spiral with specified spacing, line width and diameter
wire = []
# Create these with numpy
teta = np.linspace(0, num_turns * 2 * np.pi, 3600)
radius = spacing * teta
x = radius * np.cos(teta)
y = radius * np.sin(teta)

wire = np.array([(x[i], y[i], 0) for i in range(len(teta))])


wire = np.array(wire)
plt.plot(wire[:,0], wire[:,1], linewidth=line_width)

plt.savefig("round_coil.png")

print(wire)


# Convert the wire as a 


API.export_wire("round_coil.txt", wire)