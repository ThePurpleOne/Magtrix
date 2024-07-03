# Sets up 3 coils and turns them on and off one at the time with a delay in between.

import digitalio
import board
import time
import pwmio

MODES = {
	1 : f"- CLASSIC (On-Off one by one, delay between on off only)",
	2 : f"- DELAYED (On-Off one by one, delay between each change)",
	3 : f"- PWM (On-Off with PWM one by one,  delay between on off only)",
	4 : f"- INVERSE (On-Off one by one with on default to repulse, delay between on off only)"
}

module = input("MODULE [1..4] : ")
mode = input(f"MODE [1..4] : {[MODES[i] for i in len(MODES)]} : ")
pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]

if mode == 3:
	coils = [pwmio.PWMOut(pin, frequency=1000) for pin in pins]
	for coil in coils:
		coil.duty_cycle = 0
else:
	coils = [digitalio.DigitalInOut(pin) for pin in pins]
	for coil in coils:
		coil.direction = digitalio.Direction.OUTPUT

print("STARTING TEST")


while True:
    for i in range(3):
        coils[i].duty_cycle = 6500 * 9
        print(f"Coil {i} ON")
        time.sleep(0.5)
        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
