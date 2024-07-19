# Footprint generation

This is a simple script to 2 types of coils with given parameters.

## Parameters

> Note : The coils are square.

- side_width: Width of the coil in both x and y direction.
- line_width: Width of the traces in the coil.
- spacing : Spacing between the traces.

> Note : The number of coils is determined by the side_width and spacing.

## Usage

The script can generate coils with specified layers.

The best choice on a 4 layer board is to use the top and third layers
for the main coils and second and bottom layers for the sub coils.
In a "sandwiched" configuration

```python
from square_coil import Coiler
if __name__ == "__main__":
    coiler = Coiler(side_width=8, line_width=0.3, spacing=0.2)

    coiler.create_and_save(
        name="coil",
        description="Test Coil",
        filename="top_coil",
        output_dir="outputs",
        layers=["F.Cu", "In2.Cu"],
    )

    coiler.create_and_save(
        name="coil",
        description="Test Coil",
        filename="sub_coil",
        output_dir="outputs",
        layers=["In1.Cu", "B.Cu"],
    )
```
