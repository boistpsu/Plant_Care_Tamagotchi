from gpiozero import Button

button = Button(18)

while True:
    if button.is_pressed:
        print("The button was pressed!")