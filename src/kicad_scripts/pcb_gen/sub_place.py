import pcbnew
from math import sqrt
import csv
import numpy as np

pcb_path = "magtrix/magtrix.kicad_pcb"
ref_layout_path = "sub_coils.csv"


pcb = pcbnew.LoadBoard(pcb_path)
components = pcb.GetFootprints()

# Only keep the SUB referenced components
components = [component for component in components if "SUB" in component.GetReference()]

number_of_coils = len(components)
print(f"Number of coils: {number_of_coils}")

def read_layout_csv(path):
    layout = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            layout.append(row[:-1])
    return np.array(layout)

layout = read_layout_csv(ref_layout_path)

final_arr = []
for i in range(layout.shape[0]):
    row = []
    for j in range(layout.shape[1]):
        for component in components:
            #print(f"{i} {j} {component.GetReference()} {layout[i][j]}")
            if component.GetReference() == layout[i][j]:
                row.append(component)
                break
    final_arr.append(row)


for i in range(layout.shape[0]):
    for j in range(layout.shape[1]):
        print(f"{final_arr[i][j].GetReference():^10} ", end="")
    print("")

sub_delta_x = 26
sub_delta_y = 13
sub_delta_half = 13

origin = 0, 0

for y_axis in range(layout.shape[0]):
    for x_axis in range(layout.shape[1]):
        component = final_arr[y_axis][x_axis]

        if "SUB" in component.GetReference():
            if y_axis % 2 == 0:
                pos = pcbnew.wxPointMM(
                    float(origin[0] + x_axis * sub_delta_x),
                    float(origin[1] + y_axis * sub_delta_y),
                )
            else:
                pos = pcbnew.wxPointMM(
                    float(origin[0] + x_axis * sub_delta_x - sub_delta_half),
                    float(origin[1] + y_axis * sub_delta_y),
                )
            component.SetOrientationDegrees(45)

        print(f"Moving {component.GetReference()} to {pos}")
        print(f"{component}")
        component.SetX(pos.x)
        component.SetY(pos.y)


# Save the updated PCB file
pcb.Save(pcb_path)

print("PCB file updated")
