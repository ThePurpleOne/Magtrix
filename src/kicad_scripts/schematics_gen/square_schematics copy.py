"""

Source : https://github.com/psychogenic/kicad-skip
"""

from skip import Symbol, Schematic

grid_origin = (0, 0) # Origin
unitspace = 2.54     # 100 mils


def units_to_mm(u: int):
    return u * unitspace


def to_grid(
    xunits: int,
    yunits: int,
):
    global unitspace, grid_origin
    return (
        (grid_origin[0] * unitspace) + (xunits * unitspace),
        (grid_origin[1] * unitspace) + (yunits * unitspace),
    )


def create_grid(
    based_on: Symbol,
    size: tuple,
    start_ref_count: int = 1,
):
    """
    Create a grid of given symbols, with the given number of rows and columns.

    args:
        based_on       : [Symbol] - Symbol to clone from
        number_rows    : [int]    - Number of rows
        number_cols    : [int]    - Number of columns
        start_ref_count: [int]    - Starting reference number (COMP1, COMP2, ...)
    """
    component_count = start_ref_count
    table = []

    for row in range(size[0]):
        column_component = []
        for col in range(size[1]):
            new_component = based_on.clone()

            # move this component where we want it, on the grid
            coords = to_grid(col * 7, row * 6)
            new_component.move(coords[0] - 1.27, coords[1])
            new_component.setAllReferences(f"D{component_count}")

            # keep track of LEDs we cloned
            column_component.append(new_component)

            component_count += 1

        table.append(column_component)

    return table


def create_grid_of_wires(
    sch: Schematic,
    based_on: Symbol,
    size: tuple,
    start_ref_count: int = 1,
):
    """
    Get the grid of cloned components, and wire them up, with junctions and labels.

    """

    component_table = create_grid(
        based_on=based_on,
        size=size,
        start_ref_count=start_ref_count,
    )
    row_label_prefix = "ROW"

    an_wires = []
    cath_wires = []
    # for every component, we're going to pull out the A pin and make row
    # we'll pull out K pin vertically and make columns
    for a_row in component_table:
        pu_wires = []

        cathode_wires = []
        for a_component in a_row:
            if a_component is None:
                pu_wires.append(None)
                cathode_wires.append(None)
                continue
            # depending on left or right orientation, we'll want to
            # draw our wires ou
            awire_direction = -1 if a_component.at.value[2] == 180 else 1
            kwire_direction = -1 if awire_direction == 1 else 1

            # create a wire for the cathode
            # this wire has some random position/orientation, will set
            kwire = sch.wire.new()

            # start it on the location of the K pin, using named attribs here
            kwire.start_at(a_component.pin.K)

            # we want it horizontal
            kwire.delta_y = 0
            # we want it one grid space out, in the right direction
            kwire.delta_x = kwire_direction * unitspace
            # stash the wire
            cathode_wires.append(kwire)

            # for the anode, we'll make two wires, one straight out,
            # one upward

            # from the pin
            awire = sch.wire.new()
            awire.start_at(a_component.pin.A)
            awire.delta_y = 0  # keep it horizontal
            awire.delta_x = awire_direction * unitspace

            # from the end of that first wire, up by 3
            atorow = sch.wire.new()
            atorow.start_at(awire.end.value)
            atorow.delta_x = 0  # vertical
            atorow.delta_y = units_to_mm(-3)

            # remember these wires that pull up to the row
            pu_wires.append(atorow)

        # keep all the wires in lists, by row
        an_wires.append(pu_wires)
        cath_wires.append(cathode_wires)

    # now we want a big wire joining each row together
    row_count = 0
    for rw in an_wires:
        # create a wire from last "pu" wire of the row, going past first
        join_wire = sch.wire.new()

        endwire_idx = -1
        while rw[endwire_idx] is None:
            endwire_idx -= 1

        join_wire.start_at(
            rw[endwire_idx].end.value
        )  # starts on end point of last up wire in row

        # end it a bit past the first of those pull-up wires
        firstwireidx = 0
        while rw[firstwireidx] is None:
            firstwireidx += 1
        first_wire_conn_point = rw[firstwireidx].end.value
        join_wire.end_at(
            [first_wire_conn_point[0] - units_to_mm(4), first_wire_conn_point[1]]
        )
        # lets add some junctions
        for w in rw:
            if w is None:
                continue
            junc = sch.junction.new()
            junc.move(w.end.value[0], w.end.value[1])

        # and finally, a global label attached to the end of our row joining wire
        row_count += 1
        lbl = sch.global_label.new()
        lbl.move(join_wire.end.value[0], join_wire.end.value[1])
        lbl.value = f"{row_label_prefix}_{row_count}"

    # this is what we'll return, the wires that form the columns,
    # unlabeled
    column_wires = []
    # ok, wire up the columns
    for col in range(size[1]):
        # end it a bit past the first of those pull-up wires
        firstwireidx = 0
        first_wire = cath_wires[firstwireidx][col]
        while first_wire is None:
            firstwireidx += 1
            first_wire = cath_wires[firstwireidx][col]

        lastwireidx = -1

        last_wire = cath_wires[lastwireidx][col]
        while last_wire is None:
            lastwireidx -= 1
            last_wire = cath_wires[lastwireidx][col]

        # we want a wire that goes down from first to past the bottom one
        join_wire = sch.wire.new()
        join_wire.start_at(first_wire.end.value)
        join_wire.delta_x = 0
        join_wire.delta_y = (
            last_wire.end.value[1] - first_wire.end.value[1]
        ) + units_to_mm(4)

        # make it visible by playing with the width and style a bit
        join_wire.stroke.width.value = 0.4
        join_wire.stroke.type.value = "dot"

        column_wires.append(join_wire)
        # add some junctions
        for rowidx in range(1, size[0]):
            if cath_wires[rowidx][col] is None:
                continue
            end_coords = cath_wires[rowidx][col].end.value
            junc = sch.junction.new()
            junc.move(end_coords[0], end_coords[1])

    return column_wires


def create_xy_grid(
    sch: Schematic,
    based_on: Symbol,
    size: tuple = (10, 10),
    start_ref_count: int = 1,
):
    column_wires = create_grid_of_wires(
        sch=sch,
        based_on=based_on,
        size=size,
        start_ref_count=start_ref_count,
    )

    col_count = 0
    for join_wire in column_wires:
        # add a global label
        lbl = sch.global_label.new()
        lbl.move(join_wire.end.value[0], join_wire.end.value[1])
        lbl.value = f"COL_{col_count+1}"
        col_count += 1

    print(f"Done: created a {size[0]}x{size[1]} grid")


if __name__ == "__main__":
    # schematics_filename = input("Path to a schematic with a LED in it (called DSOMETHING): ")
    schematics_filename = "test_project/test_project.kicad_sch"

    if schematics_filename is not None and len(schematics_filename):
        schem = Schematic(schematics_filename)

        components = schem.symbol.reference_startswith("D")
        if not len(components):
            print("No 'D*' components found in schem")
        else:
            base_component = components[0]
            print(f"Using diode {base_component.property.Reference.value}\n\n")

            size = input("Enter size of grid (e.g. 10x10) : ")
            size = size.split("x")

            if len(size) != 2:
                print("Invalid size, defaulting to 10x10")
                size = (10, 10)

            try:
                size = (int(size[0]), int(size[1]))
            except ValueError:
                print("Invalid size, defaulting to 10x10")
                size = (10, 10)

            print(f"Creating a {size[0]}x{size[1]} grid")
            create_xy_grid(
                sch=schem,
                based_on=base_component,
                size=size,
                start_ref_count=len(components),
            )

            save_to = input("Path to save results to (empty to save to current): ")
            if save_to is not None and len(save_to):
                schem.write(save_to)
                print(f"Saved into {save_to}")
            else:
                schem.write(schematics_filename)
                print(f"Saved into {schematics_filename}")