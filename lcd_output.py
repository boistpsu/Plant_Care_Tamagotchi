import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Resources", "drivers"))
from lib import LCD_2inch
from PIL import Image
import pygame as pg

disp = LCD_2inch.LCD_2inch()
disp.Init()
disp.clear()

lcd_frame = 0


def send_to_lcd(surface):
    global lcd_frame
    lcd_frame += 1
    if lcd_frame < 10:
        return
    lcd_frame = 0

    raw = pg.image.tostring(surface, 'RGB')
    img = Image.frombytes('RGB', (320, 240), raw)
    img = img.rotate(90, expand=True)
    disp.ShowImage(img)