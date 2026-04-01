from gpiozero import Button
from time import sleep

button = Button(18)
while True:
    val = button.is_pressed()
    if val == True:
        print("The button was pressed!")
    print("...")