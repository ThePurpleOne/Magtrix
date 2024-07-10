from KicadModTree import *

if __name__ == "__main__":
	VERTICAL_LEN = 70 # mm
	HORIZONTAL_LEN = 70 # mm
	MARGIN = 1 # mm
	#TRACE_WIDTH = 0.254 * 2 # mm
	TRACE_WIDTH = 0.254 * 4 # mm
	TRACE_SPACING = 0.254 # mm
	VERTICAL = False

	VIA_DIAMETER = 0.3 # mm
	VIA_DRILL = 0.15 # mm

	if VERTICAL:
		NUMBER_OF_TRACES = VERTICAL_LEN / (TRACE_WIDTH + TRACE_SPACING)
	else:
		NUMBER_OF_TRACES = HORIZONTAL_LEN / (TRACE_WIDTH + TRACE_SPACING)

	footprint_name = "coil_test"

	# print some info
	print(f"Vertical length: {VERTICAL_LEN}")
	print(f"Horizontal length: {HORIZONTAL_LEN}")
	print(f"Trace width: {TRACE_WIDTH}")
	print(f"Trace spacing: {TRACE_SPACING}")
	print(f"Number of traces: {NUMBER_OF_TRACES}")

	print(f"{'-' * 10}")
	print(f"CREATING FOOTPRINT: {footprint_name}")

	# ! init kicad footprint
	kicad_mod = Footprint(footprint_name)
	kicad_mod.setDescription("A example footprint")
	kicad_mod.setTags("example")

	# ! set general values
	kicad_mod.append(Text(type="reference", text="REF**", at=[0, -3], layer="F.SilkS"))
	kicad_mod.append(Text(type="value", text=footprint_name, at=[1.5, 3], layer="F.Fab"))

	# ! Create the outline
	# Create the vertical outline in silk screen
	kicad_mod.append(
			RectLine(
				start=[0, 0], 
				end=[HORIZONTAL_LEN, VERTICAL_LEN],
				thickness=0.1,
				layer="F.SilkS"
				)
		)


	# ! Create the traces
	# Need to take the spacing and width into account
	if VERTICAL:
		for i in range(int(NUMBER_OF_TRACES)):
			x = i * (TRACE_SPACING + TRACE_WIDTH) + MARGIN
			# Dont do the last one if there is not enough space with margin
			if x + TRACE_WIDTH < HORIZONTAL_LEN - MARGIN:
				kicad_mod.append(
						Line(
							start=[x, 0 + MARGIN], 
							end=[x, VERTICAL_LEN - MARGIN], 
							width=TRACE_WIDTH, layer="F.Cu"
							)
					)
	else:
		for i in range(int(NUMBER_OF_TRACES)):
			y = i * (TRACE_SPACING + TRACE_WIDTH) + MARGIN
			if y + TRACE_WIDTH < VERTICAL_LEN - MARGIN:
				kicad_mod.append(
						Line(
							start=[0 + MARGIN, y], 
							end=[HORIZONTAL_LEN - MARGIN, y], 
							width=TRACE_WIDTH, layer="F.Cu"
							)
					)
				# Create a pth pad between Back an Front copper
				kicad_mod.append(
						Pad(
							number=i,
							type=Pad.TYPE_THT,
							shape=Pad.SHAPE_CIRCLE,
							at=[0, y],
							size=[VIA_DIAMETER, VIA_DIAMETER],
							drill=VIA_DRILL,
							layers=Pad.LAYERS_THT,
							)
					)

				
	

	file_handler = KicadFileHandler(kicad_mod)
	file_handler.writeFile(f"{footprint_name}.kicad_mod")




	## create silscreen
	#kicad_mod.append(RectLine(start=[-2, -2], end=[5, 2], layer="F.SilkS"))

	## create courtyard
	#kicad_mod.append(RectLine(start=[-2.25, -2.25], end=[5.25, 2.25], layer="F.CrtYd"))



	## create pads
	#kicad_mod.append(
	#	Pad(
	#		number=1,
	#		type=Pad.TYPE_THT,
	#		shape=Pad.SHAPE_RECT,
	#		at=[0, 0],
	#		size=[2, 2],
	#		drill=1.2,
	#		layers=Pad.LAYERS_THT,
	#	)
	#)


	#kicad_mod.append(
	#	Pad(
	#		number=2,
	#		type=Pad.TYPE_THT,
	#		shape=Pad.SHAPE_CIRCLE,
	#		at=[3, 0],
	#		size=[2, 2],
	#		drill=1.2,
	#		layers=Pad.LAYERS_THT,
	#	)
	#)


