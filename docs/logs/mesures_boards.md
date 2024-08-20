
# Sub coils
> Round sub coils between the main coils.

Drawing lots of current at 100%, reduced to 60-70% with a PWM 


Max temperature : 80°C (Thermal camera)

8mm Magnet 


## Code
```py
import digitalio
import board
import time
import pwmio

pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]

coils = [pwmio.PWMOut(pin, frequency=50000) for pin in pins]

for coil in coils:
    coil.duty_cycle = 0

print("STARTING TEST")

while True:
    for i in range(6):
        coils[i].duty_cycle = 40000
        print(f"Coil {i} ON")
        time.sleep(0.3)
        
        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
        time.sleep(0.2)

    for i in range(5, -1, -1):
        coils[i].duty_cycle = 40000
        print(f"Coil {i} ON")
        time.sleep(0.3)

        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
        time.sleep(0.2)
```

## Status
Working almost fine!


# Layered coils

> 4 layers per coil

Max temperature : 65°C (Thermal camera)


Not drawing as much current as the sub coils, PWM almost max, not moving at all from one to another...

# SUB COILS SQUARE

> Square sub coils between the main coils, everythin is the same size and square.

Max temperature : 85°C after a long test (Thermal camera)

8mm Magnet

## Code
```py
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
        time.sleep(0.4)
        
        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
        #time.sleep(0.2)

    for i in range(4, -1, -1): # 4 to skip the second F
        coils[i].duty_cycle = 65000
        print(f"Coil {i} ON")
        time.sleep(0.3)

        coils[i].duty_cycle = 0
        print(f"Coil {i} OFF")
        #time.sleep(0.2)
```

## Status

Working really well, excepted the F position where it cannot hold enough the magnet