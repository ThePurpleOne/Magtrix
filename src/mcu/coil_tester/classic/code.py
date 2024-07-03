# Sets up 3 coils and turns them on and off one at the time with a delay in between.

import digitalio
import board
import time
import pwmio

pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]


#coils = [digitalio.DigitalInOut(pin) for pin in pins]
coils = [pwmio.PWMOut(pin, frequency=100000) for pin in pins]

for coil in coils:
    coil.duty_cycle = 0

print("STARTING TEST")


while True:
    #for i in range(2, -1, -1):
    for i in range(3):
        coils[i].duty_cycle = 6500 * 9
        coils[i + 3].duty_cycle = 6500 * 9
        print(f"Coil {i} ON")
        time.sleep(0.1)
        
        coils[i].duty_cycle = 0
        coils[i + 3].duty_cycle = 0
        print(f"Coil {i} OFF")
        time.sleep(0.1)
    
	#coils[1].duty_cycle = 6500 * 9
	#print(f"Coil {1} ON")
	#time.sleep(0.5)
	#coils[1].duty_cycle = 0
	#print(f"Coil {1} OFF")
