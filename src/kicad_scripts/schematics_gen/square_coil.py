"""
Author : Jonas Stirnemann
Date : 11/07/2024
Description : This will create a schematics with a matrix of n*m coils

Sources:
- https://www.youtube.com/watch?v=EP1GtsZ2VfM
- https://github.com/psychogenic/kicad-skip
- https://github.com/psychogenic/kicad-skip/blob/main/src/skip/examples/charlieplex.py
"""
import os
import sys

# Ensure that the KICAD_SYMBOL_DIR environment variable is set
# to point to the location of the KiCad symbol library
if 'KICAD_SYMBOL_DIR' not in os.environ:
    os.environ['KICAD_SYMBOL_DIR'] = '/usr/share/kicad/symbols'

# Import KiCad Python module
from pcbnew import *

# Initialize KiCad project
project_path = "path/to/your/project"
project_name = "your_project_name"
sch_file = os.path.join(project_path, f"{project_name}.kicad_sch")

# Create a new schematic
sclib = SCH_LIB(SCH_COMPONENT_LIB)
sch = SCH_SHEET()
sclib.Add(sch)

# Define symbols and positions
symbols = [
    {"lib": "Device", "name": "R", "ref": "R1", "x": 50, "y": 50},
    {"lib": "Device", "name": "C", "ref": "C1", "x": 100, "y": 100},
    {"lib": "Device", "name": "U", "ref": "U1", "x": 150, "y": 150},
]

# Function to add symbol
def add_symbol(sch, lib_name, symbol_name, ref, x, y):
    lib = SCH_LIB_PART_LIB(lib_name)
    symbol = SCH_COMPONENT(lib, symbol_name)
    symbol.Reference().SetText(ref)
    symbol.SetPosition(wxPoint(x * 10000, y * 10000))
    sch.Add(symbol)

# Add symbols to schematic
for symbol in symbols:
    add_symbol(sch, symbol["lib"], symbol["name"], symbol["ref"], symbol["x"], symbol["y"])

# Define labels and positions
labels = [
    {"name": "LABEL1", "x": 60, "y": 50},
    {"name": "LABEL2", "x": 110, "y": 100},
    {"name": "LABEL3", "x": 160, "y": 150},
]

# Function to add label
def add_label(sch, label_name, x, y):
    label = SCH_TEXT(sch)
    label.SetText(label_name)
    label.SetPosition(wxPoint(x * 10000, y * 10000))
    sch.Add(label)

# Add labels to schematic
for label in labels:
    add_label(sch, label["name"], label["x"], label["y"])

# Save schematic
sch.Save(sch_file)

print(f"Schematic saved to {sch_file}")
