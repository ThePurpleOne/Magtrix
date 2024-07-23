"""

Source : https://github.com/psychogenic/kicad-skip
"""

from skip import Symbol, Schematic
from typing import List, Tuple
import os
import logging


class ComponentMatrixMaker:
    def __init__(
        self,
        schematics_filename: str,
        component_prefix: str,
        size: Tuple[int, int],
    ) -> None:
        self.setup_logger()
        self.logger = logging.getLogger("logger")

        self.grid_origin = (0, 0)  # Origin
        self.unitspace = 2.54  # 100 mils

        self.schematics = self.get_schematics(schematics_filename)
        self.og_component = self.get_component(component_prefix)
        self.size = self.get_size(size)

        self.component_matrix = self.__create_component_matrix(
            based_on=self.og_component,
            size=self.size,
            start_ref_count=1,
        )

        self.components_n_wires = self.__create_full_matrix(
            sch=self.schematics,
            size=self.size,
            component_matrix=self.component_matrix,
        )

        self.__create_final_matrix(
            sch=self.schematics,
            full_matrix=self.components_n_wires,
        )

    def get_schematics(self, schematics_filename: str):
        if schematics_filename is not None and len(schematics_filename):
            try:
                sch = Schematic(schematics_filename)
            except FileNotFoundError:
                self.perror("File not found")
                exit(-1)
            except Exception as e:
                self.perror(f"Error: {e}")
                exit(-1)

            self.logger.info(f"Loaded {schematics_filename}")
            return sch

        else:
            self.logger.error("No schematics file provided")
            exit(-1)

    def get_component(
        self,
        component_prefix: str,
    ):
        components = self.schematics.symbol.reference_startswith(component_prefix)
        if not len(components):
            self.logger.error(
                f"No components found with {component_prefix} prefix \n\t(The schematics should have at least 1 component with this prefix)"
            )
            exit(-1)
        else:
            self.logger.info(
                f"Using component {components[0].property.Reference.value}"
            )
            return components[0]

    def get_size(self, size: tuple):
        """
        Validate the size of the grid
        Min = 1x1
        Max = 100x100
        """
        if len(size) == 2 and all(isinstance(x, int) for x in size):
            if size[0] < 1 or size[1] < 1:
                self.logger.warning(f"{size} is too small, defaulting to 5x5 (MIN 1x1)")
                return (5, 5)
            elif size[0] > 100 or size[1] > 100:
                self.logger.warning(
                    f"{size} is too large, defaulting to 5x5 (MAX 100x100)"
                )
                return (5, 5)
            else:
                return size
        else:
            self.logger.warning(
                f"{size} is invalid, defaulting to 5x5 (NEED TUPLE (x, y))"
            )
            return (5, 5)

    def units_to_mm(self, u: int):
        return u * self.unitspace

    def to_grid(
        self,
        xunits: int,
        yunits: int,
    ):
        unitspace, grid_origin = self.unitspace, self.grid_origin
        return (
            (grid_origin[0] * unitspace) + (xunits * unitspace),
            (grid_origin[1] * unitspace) + (yunits * unitspace),
        )

    def __create_component_matrix(
        self,
        based_on: Symbol,
        size: Tuple[int, int],
        start_ref_count: int,
    ):
        """
        Create a grid of given symbols, with the given size

        args:
                based_on       : [Symbol] - Symbol to clone from
                number_rows    : [int]    - Number of rows
                number_cols    : [int]    - Number of columns
                start_ref_count: [int]    - Starting reference number (COMP1, COMP2, ...)
        returns
                table          : [list]   - 2D list of cloned components
        """
        component_count = start_ref_count
        matrix = []

        for row in range(size[0]):
            column_component = []
            for col in range(size[1]):
                new_component = based_on.clone()

                # move this component where we want it, on the grid
                coords = self.to_grid(col * 7, row * 6)
                new_component.move(coords[0] - 1.27, coords[1])
                new_component.setAllReferences(f"D{component_count}")

                column_component.append(new_component)
                component_count += 1

            matrix.append(column_component)

        return matrix

    def __create_full_matrix(
        self,
        sch: Schematic,
        size: tuple,
        component_matrix,
    ):
        """
        Get the grid of cloned components, and wire them up, with junctions and labels.

        """

        row_label_prefix = "ROW"

        an_wires = []
        cath_wires = []
        # for every component, we're going to pull out the A pin and make row
        # we'll pull out K pin vertically and make columns
        for a_row in component_matrix:
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
                kwire.delta_x = kwire_direction * self.unitspace
                # stash the wire
                cathode_wires.append(kwire)

                # for the anode, we'll make two wires, one straight out,
                # one upward

                # from the pin
                awire = sch.wire.new()
                awire.start_at(a_component.pin.A)
                awire.delta_y = 0  # keep it horizontal
                awire.delta_x = awire_direction * self.unitspace

                # from the end of that first wire, up by 3
                atorow = sch.wire.new()
                atorow.start_at(awire.end.value)
                atorow.delta_x = 0  # vertical
                atorow.delta_y = self.units_to_mm(-3)

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
                [
                    first_wire_conn_point[0] - self.units_to_mm(4),
                    first_wire_conn_point[1],
                ]
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
            ) + self.units_to_mm(4)

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

    def __create_final_matrix(
        self,
        sch: Schematic,
        full_matrix: List,
    ):
        col_count = 0
        for join_wire in full_matrix:
            # add a global label
            lbl = sch.global_label.new()
            lbl.move(join_wire.end.value[0], join_wire.end.value[1])
            lbl.value = f"COL_{col_count+1}"
            col_count += 1

        self.logger.info(f"Created final matrix {self.size}")

    def save_to_schematics(self, save_to: str):
        if save_to is not None and len(save_to):
            if not save_to.endswith(".kicad_sch"):
                save_to = f"{save_to}.kicad_sch"

            if not os.path.exists(os.path.dirname(save_to)):
                os.makedirs(os.path.dirname(save_to))

            self.schematics.write(save_to)
            self.logger.info(f"Saved into {save_to}")
        else:
            self.schematics.write(self.schematics.filename)
            self.logger.info(f"Saved into {self.schematics.filename}")

    def setup_logger(self, level: int = logging.DEBUG):
        class CustomFormatter(logging.Formatter):
            grey = "\x1b[38;20m"
            green = "\x1b[32;20m"
            yellow = "\x1b[33;20m"
            red = "\x1b[31;20m"
            bold_red = "\x1b[31;1m"
            reset = "\x1b[0m"
            format = "[%(asctime)s] |%(levelname)s| (%(filename)s@%(lineno)4d) : %(message)s "

            FORMATS = {
                logging.DEBUG: grey + format + reset,
                logging.INFO: green + format + reset,
                logging.WARNING: yellow + format + reset,
                logging.ERROR: red + format + reset,
                logging.CRITICAL: bold_red + format + reset,
            }

            def format(self, record):
                log_fmt = self.FORMATS.get(record.levelno)
                formatter = logging.Formatter(log_fmt)
                return formatter.format(record)

        logger = logging.getLogger("logger")
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        ch.setFormatter(CustomFormatter())

        logger.addHandler(ch)


if __name__ == "__main__":
    # schematics_filename = input("Path to a schematic with a LED in it (called DSOMETHING): ")
    in_file = out_file = "test_project/test_project.kicad_sch"
    # out_file = "test_project/test_project2.kicad_sch"

    cmm = ComponentMatrixMaker(
        schematics_filename=in_file,
        component_prefix="D",
        size=(10, 10),
    )

    cmm.save_to_schematics(save_to=out_file)  # Save to original
