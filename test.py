from gpiozero import Button

button = Button(18)
print(button)
button.wait_for_press()
print("button was pressed")
print(button)