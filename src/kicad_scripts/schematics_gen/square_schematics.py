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
        component_prefix1: str,
        component_prefix2: str,
        size: Tuple[int, int],
    ) -> None:
        self.setup_logger()
        self.logger = logging.getLogger("logger")

        self.unitspace = 1.27  # 50 mils
        self.grid_origin = (self.unitspace * 40, self.unitspace * 30)  # Origin

        self.schematics = self.get_schematics(schematics_filename)
        self.og_component1 = self.get_component(component_prefix1)
        self.og_component2 = self.get_component(component_prefix2)
        self.size = self.get_size(size)

        self.component_matrix = self.__create_component_matrix(
            based_on=(self.og_component1, self.og_component2),
            prefixes=(component_prefix1, component_prefix2),
            size=self.size,
            start_ref_count=1,
        )

        self.components_n_wires = self.__add_wires_to_components(
            sch=self.schematics,
            size=self.size,
            component_matrix=self.component_matrix,
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
                f"Using component {components[0].property.Reference.value} as base"
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
        prefixes: Tuple[str, str],
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
        component_count1 = start_ref_count
        component_count2 = start_ref_count
        c1, c2 = based_on
        pf1, pf2 = prefixes
        matrix = []

        for row in range(size[0]):
            column_component = []
            for col in range(size[1]):
                if (col % 2 == 0 and row % 2 == 0) or (col % 2 == 1 and row % 2 == 1):
                    new_component = c1.clone()

                    # move this component where we want it, on the grid
                    coords = self.to_grid(col * 14, row * 14)
                    new_component.move(coords[0] - 1.27, coords[1])
                    new_component.setAllReferences(f"{pf1}{component_count1}")

                    column_component.append(new_component)
                    component_count1 += 1
                else:
                    new_component = c2.clone()

                    # move this component where we want it, on the grid
                    coords = self.to_grid(col * 14, row * 14)
                    new_component.move(coords[0] - 1.27, coords[1])
                    new_component.setAllReferences(f"{pf2}{component_count2}")

                    column_component.append(new_component)
                    component_count2 += 1

            matrix.append(column_component)

        self.logger.info(f"Created component matrix {size}")

        return matrix

    def __add_wires_to_components(
        self,
        sch: Schematic,
        size: tuple,
        component_matrix,
    ):
        """
        Add wires to the components in the matrix
        """

        last_row_col_wires = []
        # For each component in the matrix and it's x, y
        for row_idx, comp_row in enumerate(component_matrix):
            for comp in comp_row:
                # ! Get away wire from component A pin
                get_away_a = sch.wire.new()
                get_away_a.start_at(comp.pin.A)
                get_away_a.delta_y = self.unitspace * -2
                get_away_a.delta_x = 0

                # ! For each of these get away wires, we create a junction point
                junc = sch.junction.new()
                junc.move(get_away_a.end.value[0], get_away_a.end.value[1])

                # ! Get away wire from component B pin
                b_wire = sch.wire.new()
                b_wire.start_at(comp.pin.B)
                b_wire.delta_y = self.unitspace * 2
                b_wire.delta_x = 0

                # ! Add vertical wire from end of get away to the soon to be column wire
                b_wire_row = sch.wire.new()
                b_wire_row.start_at(b_wire.end.value)
                b_wire_row.delta_y = 0
                b_wire_row.delta_x = self.unitspace * 6

                # ! For each of these get away wires, we create a junction point
                junc = sch.junction.new()
                junc.move(b_wire.end.value[0], b_wire.end.value[1])

                # ! Create column wires
                b_wire_col = sch.wire.new()
                b_wire_col.start_at(b_wire_row.end.value)
                b_wire_col.delta_y = self.unitspace * 14
                b_wire_col.delta_x = 0

                if row_idx == size[0] - 1:
                    last_row_col_wires.append(b_wire_col)

            # ! In the last row index
            # ! Add a label for each column at the end
            if row_idx == size[0] - 1:
                for idx, wire in enumerate(last_row_col_wires):
                    lbl = sch.global_label.new()
                    lbl.move(wire.end.value[0], wire.end.value[1])
                    lbl.value = f"COL_{idx}"

            # ! If its the first component in the row
            # ! Draw a wire from the A - x 10 unit to the last component in the row
            # Draw horizontal wire
            row_wire = sch.wire.new()
            # This gate away wire is the last's component in the row
            row_wire.start_at(get_away_a.end.value)
            row_wire.delta_y = 0
            delta_between_components = 14
            row_wire.delta_x = -self.unitspace * (delta_between_components * (size[1]))

            # ! Draw a global label at the end of the row wire with the row number
            lbl = sch.global_label.new()
            lbl.move(row_wire.end.value[0], row_wire.end.value[1])
            lbl.value = f"ROW_{row_idx}"

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
    in_file = out_file = "../test_project/test_project.kicad_sch"

    cmm = ComponentMatrixMaker(
        schematics_filename=in_file,
        component_prefix1="TOP",
        component_prefix2="SUB",
        size=(16, 16),
    )

    cmm.save_to_schematics(save_to=out_file)
