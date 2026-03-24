import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Resources", "drivers"))
from lib import LCD_2inch
from PIL import Image
import pygame as pg
import threading

disp = LCD_2inch.LCD_2inch()
disp.Init()
disp.clear()

_latest_image = None
_lock = threading.Lock()

def _lcd_worker():
    while True:
        with _lock:
            img = _latest_image
        if img is not None:
            disp.ShowImage(img)

thread = threading.Thread(target=_lcd_worker, daemon=True)
thread.start()

def send_to_lcd(surface):
    global _latest_image
    raw = pg.image.tostring(surface, 'RGB')
    img = Image.frombytes('RGB', (320, 240), raw)
    img = img.rotate(90, expand=True)
    with _lock:
        _latest_image = img