from gpiozero import Button

button = Button(18)
while True:
    if not button.value:
        print("The button was pressed!")