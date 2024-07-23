# Testing the 4 boards
 
import digitalio
import board
import time
import pwmio


pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]


coils = [pwmio.PWMOut(pin, frequency=50000) for pin in pins]


for coil in coils:
    coil.duty_cycle = 0


print("STARTING TEST")

ACTIVE_TIME = 0.5
INACTIVE_TIME = 0.1


while True:
    for i in range(6):
        coils[i].duty_cycle = 65000
        print(f"Coil {i} ON")
        time.sleep(1)
        
        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
        #time.sleep(1)

    for i in range(4, -1, -1): # 4 to skip the second F
        coils[i].duty_cycle = 65000
        print(f"Coil {i} ON")
        time.sleep(1)

        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
        #time.sleep(1)