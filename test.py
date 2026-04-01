from gpiozero import Button

button = Button(18)
print(button)
state = True
while state:
    val = button.is_pressed()
    if val == True:
        print("button was pressed")
        state = False