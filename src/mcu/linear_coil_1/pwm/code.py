# Sets up 3 coils and turns them on and off one at the time with a delay in between.

import digitalio
import board
import time
import pwmio

pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]


coils = [pwmio.PWMOut(pin, frequency=1000) for pin in pins]

for coil in coils:
    coil.duty_cycle = 0

while True:
    for i in range(3):
        coils[i].duty_cycle = 65000
        print(f"Coil {i} ON")
        time.sleep(0.3)
        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")