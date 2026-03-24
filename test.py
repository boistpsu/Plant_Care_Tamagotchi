import os, sys
sys.path.append(os.path.expanduser('~/LCD_Module_RPI_code/RaspberryPi/python/lib'))
from lib import LCD_2inch
from PIL import Image, ImageDraw

disp = LCD_2inch.LCD_2inch()
disp.Init()
disp.clear()

# draw a simple red rectangle
img = Image.new('RGB', (320, 240), (255, 0, 0))
disp.ShowImage(img)