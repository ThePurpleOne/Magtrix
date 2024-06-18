import pcbnew

if __name__ == "__main__":
    VERTICAL_LEN = 60 # mm
    HORIZONTAL_LEN = 60 # mm
    MARGIN = 1 # mm
    TRACE_WIDTH = 0.0254 * 4 # mm
    TRACE_SPACING = 0.0254 # mm
    VERTICAL = False

    VIA_DIAMETER = 0.3 # mm
    VIA_DRILL = 0.15 # mm

    if VERTICAL:
        NUMBER_OF_TRACES = VERTICAL_LEN / (TRACE_WIDTH + TRACE_SPACING)
    else:
        NUMBER_OF_TRACES = HORIZONTAL_LEN / (TRACE_WIDTH + TRACE_SPACING)

    board_name = "coil_test"

    # print some info
    print(f"Vertical length: {VERTICAL_LEN}")
    print(f"Horizontal length: {HORIZONTAL_LEN}")
    print(f"Trace width: {TRACE_WIDTH}")
    print(f"Trace spacing: {TRACE_SPACING}")
    print(f"Number of traces: {NUMBER_OF_TRACES}")

    print(f"{'-' * 10}")
    print(f"CREATING BOARD: {board_name}")


	# 