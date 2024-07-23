# Sets up 3 coils and turns them on and off one at the time with a delay in between.

import digitalio
import board
import time


pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]


coils = [digitalio.DigitalInOut(pin) for pin in pins]

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT
    coil.value = True

#coils[3].value = True


print("STARTING TEST")

ACTIVE_TIME = 0.2
INACTIVE_TIME = 0.3

while True:

    for i in range(2):
        coils[i].value = False
        print(f"Coil {i} ON")
        time.sleep(ACTIVE_TIME)
        coils[i].value = True
        print(f"Coil {i} OFF")
        time.sleep(INACTIVE_TIME)