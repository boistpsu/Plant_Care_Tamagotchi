from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    print("button 1 pressed")
    sleep(1)