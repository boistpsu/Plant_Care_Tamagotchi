from gpiozero import Button

button = Button(18)
while True:
    if button.value == True:
        print("The button was pressed!")
    print("...")