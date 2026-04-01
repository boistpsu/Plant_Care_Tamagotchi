from gpiozero import Button

button = Button(18)
print(button)
state = True
while state:
    if button.is_pressed():
        print("button was pressed")
        state = False