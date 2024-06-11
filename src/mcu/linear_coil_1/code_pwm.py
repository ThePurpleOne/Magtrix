import digitalio
import board
import time


pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, ]


coils = [digitalio.DigitalInOut(pin) for pin in pins]

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

coils[3].value = True


print("STARTING TEST")
delay = input("How much delay ?")
delay = float(delay)
print(f"Delay: {delay} seconds")


while True:
    # Set coils 0 to 2 to true one at the time

    #print("From 0 to 2")
    #for _ in range(10):  # Do it 10 times 
    for i in range(3):
        coils[i].value = False
        print(f"Coil {i} ON")
        time.sleep(delay)
        coils[i].value = True
        print(f"Coil {i} OFF")

    #print("From 2 to 0")
    #for _ in range(10):  # Do it 10 times in reverse
    #    for i in range(3, 0, -1):
    #        coils[i].value = False
    #        print(f"Coil {i} ON")
    #        time.sleep(delay)
    #        coils[i].value = True
    #        print(f"Coil {i} OFF")
