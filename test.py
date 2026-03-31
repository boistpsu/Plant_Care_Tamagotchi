from gpiozero import Button
from time import sleep

button = Button(18)
button.wait_for_press()
print("The button was pressed!")