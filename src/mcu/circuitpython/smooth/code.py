# This will follow a path given by a list of coils 
 
import digitalio
import board
import time
import pwmio


pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]




coils = [pwmio.PWMOut(pin, frequency=50000) for pin in pins]

for coil in coils:
    coil.duty_cycle = 0
    
path = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]


while True:
    print(f"Launching Path : {path}")

    val = 65000
    count = 0

    for i, cell_index in enumerate(path):
        
        while count < 65000:
            coils[path[i]].duty_cycle = count
            count += 5000
            print(f"Coil {path[i]} {count}")
            time.sleep(0.05)

        coils[path[i]].duty_cycle = 0
        count = 0

        #time.sleep(0.5)
        print(f"Coil {i} OFF")