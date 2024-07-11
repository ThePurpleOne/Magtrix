"""
Author : Jonas Stirnemann
Date : 11/07/2024
Description : This allows us to generate simple square coils as Kicad footprints

Sources:
- https://www.youtube.com/watch?v=cGJYCe6mGR0
- https://github.com/cst0/kicad-coil-generator/tree/master
- https://github.com/joards/Simple-Planar-Coil-Generator/tree/master
- https://kicad-footprint-generator.readthedocs.io/en/latest/KicadModTree.nodes.base.html#module-KicadModTree.nodes.base.Pad
"""

import KicadModTree as kmt
from typing import List, Tuple


class Coiler:
	def __init__(
		self,
		side_width: int,
		line_width: float = 0.3,
		spacing: float = 0.2,
	):
		self.side_width = side_width
		self.spacing = spacing
		self.line_width = line_width
		self.displacement = 0.7  # How much is the pad displaced

	def create_and_save(
		self,
		name: str,
		description: str,
		output_path: str,
	):
		"""
		This will create the coil and save it to a file
		"""
		front = self.create_coil_segments(layer="F.Cu")
		back = self.rotate_segments(self.create_coil_segments(layer="B.Cu"), 90)

		segments = [front, back]

		pads = self.create_single_coil_pads(
			start_point=(0, 0),
			end_point=(self.side_width, -self.side_width),
		)
		footprint = self.construct_footprint(name, description, segments, pads)
		self.save_footprint(footprint, output_path)

	def rotate_segments(self, segment: List[kmt.Line], angle: int) -> List[kmt.Line]:
		"""
		This will rotate the segment by the angle
		with
		rotate(angle, origin=(0, 0), use_degrees=True)
		"""

		rotated_segments = []
		for seg in segment:
			rotated_segments.append(seg.rotate(angle, origin=(0, 0), use_degrees=True))

		return rotated_segments


	def create_coil_segments(self, layer) -> List[kmt.Line]:
		"""
		This will create the actual segments of the coil.
		This uses kmt.Line to create the segments of the coil.
		returns : segments of the coil
		"""

		# Get the number of turns we can execute considering
		# the spacing and the line width
		number_of_turns = int(self.side_width / (self.line_width + self.spacing)) - 1

		points = []

		# In order to be connected properly to the pad
		# that we hard coded as a bit further
		# We need to connect the first segment to the pad

		# Start point
		points.append((self.side_width + self.displacement, -self.side_width))

		for i in range(number_of_turns):
			r = self.side_width - i * (self.line_width + self.spacing)
			next_r = r - (self.line_width + self.spacing)

			# Penultimate segment, cut it short to reach the y = 0
			# If it's the last segment, we need to connect it to the middle pad
			if i == (number_of_turns - 1):
				turn_points = [
					(-r, -r),
					(-r, r),
					(r, r),
					(r, 0),
					(0, 0),
				]
			else:
				turn_points = [
					(-r, -r),
					(-r, r),
					(r, r),
					(r, -next_r),
				]

			points.extend(turn_points)

		lines = []
		for i in range(len(points) - 1):
			lines.append(
				kmt.Line(
					start=points[i],
					end=points[i + 1],
					width=self.line_width,
					layer=layer,
				)
			)

		return lines

	def create_single_coil_pads(
		self,
		start_point: Tuple[int, int],
		end_point: Tuple[int, int],
	) -> List[kmt.Pad]:
		"""
		This will create the pads of the coil, On in the center and one at the beginning
		This will always be a THT pad connecting all layers
		"""
		pad_type = kmt.Pad.TYPE_THT
		pad_layer = kmt.Pad.LAYERS_THT
		pad_shape = kmt.Pad.SHAPE_RECT
		drill = 0.3
		drill_kw = dict()

		pads = []

		# Make the end point a little further to avoid to have the pad
		# too close to the last segment
		end_point = end_point[0] + self.displacement, end_point[1]

		for i, pos in enumerate([start_point, end_point]):
			pad = kmt.Pad(
				number=i + 1,
				type=pad_type,
				shape=pad_shape,
				at=pos,
				size=[0.6, 0.6],
				drill=drill,
				layers=pad_layer,
				**drill_kw,
			)
			pads.append(pad)

		return pads

	def create_dual_coil_pads(
		self,
		start_point: Tuple[int, int],
		end_point: Tuple[int, int],
	) -> List[kmt.Pad]:
		"""
		This will create the pads of the coil, On in the center and one at the beginning
		This will always be a THT pad connecting all layers
		"""
		pad_type = kmt.Pad.TYPE_THT
		pad_layer = kmt.Pad.LAYERS_THT
		pad_shape = kmt.Pad.SHAPE_RECT
		drill = 0.3
		drill_kw = dict()

		pads = []

		# Make the end point a little further to avoid to have the pad
		# too close to the last segment
		end_point = end_point[0] + self.displacement, end_point[1]

		for i, pos in enumerate([start_point, end_point]):
			pad = kmt.Pad(
				number=i + 1,
				type=pad_type,
				shape=pad_shape,
				at=pos,
				size=[0.6, 0.6],
				drill=drill,
				layers=pad_layer,
				**drill_kw,
			)
			pads.append(pad)

		return pads

	def construct_footprint(
		self,
		name: str,
		description: str,
		segments: List[List[kmt.Line]],
		pads: List[kmt.Pad],
	) -> kmt.Footprint:
		"""
		This will create the actual footprint
		with the segments and the pads
		"""
		fp = kmt.Footprint(name)
		fp.setDescription(description)

		# add some text: reference and value
		fp.append(kmt.Text(type="reference", text="REF**", at=[0, -2], layer="F.SilkS"))
		fp.append(kmt.Text(type="value", text=name, at=[1.5, 2], layer="F.Fab"))

		for segs in segments:
			for seg in segs:
				fp.append(seg)

		for pad in pads:
			fp.append(pad)

		return fp

	def save_footprint(self, footprint: kmt.Footprint, file_name: str):
		"""
		This will save the footprint to a file
		"""
		if not file_name.endswith(".kicad_mod"):
			file_name = file_name + ".kicad_mod"

		fh = kmt.KicadFileHandler(footprint)
		fh.writeFile(file_name)

		print(f"Footprint saved to {file_name}")


if __name__ == "__main__":
	coiler = Coiler(side_width=8, line_width=0.3, spacing=0.2)

	coiler.create_and_save(
		name="TEST",
		description="Test Coil",
		output_path="output/test_mine",
	)
