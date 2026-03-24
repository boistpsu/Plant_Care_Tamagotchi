import os, sys
sys.path.insert(0, os.path.expanduser('~/LCD_Module_RPI_code/RaspberryPi/python/lib'))
sys.path.insert(0, os.path.expanduser('~/LCD_Module_RPI_code/RaspberryPi/python'))
from lib import LCD_2inch
from PIL import Image, ImageDraw

disp = LCD_2inch.LCD_2inch()
disp.Init()
disp.clear()

img = Image.new('RGB', (320, 240), (255, 0, 0))
disp.ShowImage(img)