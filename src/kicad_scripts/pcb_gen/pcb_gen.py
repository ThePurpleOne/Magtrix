import pcbnew
from math import sqrt
import csv

pcb_path = "../test_project/test_project.kicad_pcb"
ref_layout_path = "../test_project/coils_layout.csv"


# Load the PCB file
pcb = pcbnew.LoadBoard(pcb_path)


# Get a list of every components on the PCB
components = pcb.GetFootprints()

print(f"Found {len(components)} components")
number_of_coils = len(components)
nb_row_col = int(sqrt(number_of_coils))


# Read the layout csv file as a 2d array, rows are separated by newlines
# and columns are separated by commas
def read_layout_csv(path):
    layout = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            layout.append(row[:-1])
    return layout


layout = read_layout_csv(ref_layout_path)


final_arr = []
# For each component, find the corresponding position from the ref layout array
for i in range(nb_row_col):
    row = []
    for j in range(nb_row_col):
        for component in components:
            if component.GetReference() == layout[i][j]:
                row.append(component)
                break
    final_arr.append(row)


## Print the sorted components as a 2D array
for i in range(nb_row_col):
    for j in range(nb_row_col):
        print(f"{final_arr[i][j].GetReference():^10} ", end="")
    print("")


# Move the first component to a new position
new_position = pcbnew.wxPointMM(float(200), float(200))

# Save the updated PCB file
# pcb.Save(pcb_path)

print("PCB file updated")
