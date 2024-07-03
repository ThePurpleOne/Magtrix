# Sets up 3 coils and turns them on and off one at the time with a delay in between.

import digitalio
import board
import time


pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]


coils = [digitalio.DigitalInOut(pin) for pin in pins]

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

coils[3].value = True


print("STARTING TEST")

flag_toggle = False
DELAY = 0.5
while True:

    for _ in range(60):  
        if flag_toggle: # ! ONE WAY
            for i in range(3):
                coils[i].value = False
                print(f"Coil {i} ON")
                time.sleep(0.5)
                coils[i].value = True
                print(f"Coil {i} OFF")
        else: # ! THE OTHER WAY
            for i in range(2, -1, -1):
                coils[i].value = False
                print(f"Coil {i} ON")
                time.sleep(0.5)
                coils[i].value = True
                print(f"Coil {i} OFF")

    flag_toggle = not flag_toggle
