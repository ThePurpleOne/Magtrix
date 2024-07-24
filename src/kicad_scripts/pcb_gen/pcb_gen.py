import pcbnew


pcb_path = "../test_project/test_project.kicad_pcb"

# Load the PCB file
pcb = pcbnew.LoadBoard(pcb_path)


# Get a list of every components on the PCB
components = pcb.GetFootprints()

print(f"Found {len(components)} components")


# Sort only by number in refereces, not the letters (there can be multiple letters)
def sort_by_ref(comp):
    return int(comp.GetReference().strip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))


sorted_comp = sorted(components, key=sort_by_ref)

for comp in sorted_comp:
    print(
        f"Component {comp.GetReference()} at position ({comp.GetPosition().x}, {comp.GetPosition().y})"
    )

# Move the first component to a new position
new_position = pcbnew.wxPointMM(float(200), float(200))

sorted_comp[0].SetX(new_position.x)
sorted_comp[0].SetY(new_position.y)

print(
    f"Component {sorted_comp[0].GetReference()} moved to position ({new_position.x}, {new_position.y})"
)

# Save the updated PCB file
pcb.Save(pcb_path)

print("PCB file updated")
