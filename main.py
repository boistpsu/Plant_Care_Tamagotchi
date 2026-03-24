# Example file showing a basic pg "game loop"
# ref: https://www.pygame.org/docs/tut/ChimpLineByLine.html

'''
NEED TO DO
- visual sprite update when low needs
    - warning banner when low needs
    - pseudo-death screen
- set up journal to show light data
- set up garden to show nutrient data

System Integration
- send button feedback to OPC server
- recieve from OPC server
( need to build RBpi)

'''

import os, math, sys
import pygame as pg

sys.path.insert(0, os.path.expanduser('~/LCD_Module_RPI_code/RaspberryPi/python/lib'))
sys.path.insert(0, os.path.expanduser('~/LCD_Module_RPI_code/RaspberryPi/python'))
from lib import LCD_2inch
from PIL import Image

img_dir = os.path.join(os.path.dirname(__file__), "Resources", "images")
WATER_MAX = 100
NUTR_MAX = 100
LIGHT_MAX = 100

def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join(img_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)

    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(data_dir, name)
    sound = pg.mixer.Sound(fullname)

    return sound

# pg setup
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pg.init()
screen = pg.Surface((320, 240))

disp = LCD_2inch.LCD_2inch()
disp.Init()
disp.clear()

# opc update
OPC_UPDATE = pg.USEREVENT + 1
pg.time.set_timer(OPC_UPDATE, 600_000)  # 600,000 ms = 10 minutes

# create the display
display = pg.Surface(screen.get_size())
#display = display.convert()
display.fill((255,255,255))

class Tama(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image("tama.jpg", None, 2)
        self.rect.midleft = (20, display.get_rect().centery)

        self.thirst = 25
        self.vitality = 75
        self.mood = 100
        self.age = 0

        self.name = "Sprout"
        self.plant_type = "Fern"

    def opc_update(self, water, nutrients, light, age):
        self.thirst = water/WATER_MAX * 100
        self.vitality = nutrients/NUTR_MAX * 100
        self.mood = light/LIGHT_MAX * 100
        self.age = int(age)

# globals
needs_font = None
needs_icon = None
status_icon = None
indicator_icon = None

def get_status(tama):
    lowest = min(tama.thirst, tama.vitality, tama.mood)
    if lowest < 25:
        return "Critical!"
    elif lowest < 50:
        return "Needs care"
    else:
        return "Doing well"

def draw_needs(surface, tama):
    global needs_font, needs_icon
    if needs_font is None:
        needs_font = pg.font.Font(None, 30)
    if needs_icon is None:
        needs_icon, _ = load_image("sprite.png", None, 1)
        icon_size = needs_font.size("A")[1]
        needs_icon = pg.transform.scale(needs_icon, (icon_size, icon_size))

    bar_width = 100
    bar_height = 20
    padding = 30
    x = surface.get_width() - bar_width - 20
    start_y = 55

    needs = [
        ("Thirst",   tama.thirst,   (100, 200, 100)),
        ("Vitality", tama.vitality, (100, 150, 255)),
        ("Mood",     tama.mood,     (255, 200,  80)),
    ]

    for i, (label, value, color) in enumerate(needs):
        y = start_y + i * (bar_height + padding)

        pg.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
        pg.draw.rect(surface, color, (x, y, int(bar_width * value / 100), bar_height))

        text = needs_font.render(label, True, (0, 0, 0))
        icon_size = needs_icon.get_width()
        label_y = y + bar_height + 2
        surface.blit(needs_icon, (x, label_y))
        remaining_x = x + icon_size + 4
        remaining_width = bar_width - icon_size - 4
        text_x = remaining_x + (remaining_width - text.get_width()) // 2
        surface.blit(text, (text_x, label_y))

def draw_above(surface, tama):
    global status_icon, needs_font
    if status_icon is None:
        status_icon, _ = load_image("sprite.png", None, 1)
        status_icon = pg.transform.scale(status_icon, (16, 16))
    if needs_font is None:
        needs_font = pg.font.Font(None, 30)

    y = 10
    day_text = needs_font.render(f"Day {tama.age}", True, (0, 0, 0))
    surface.blit(day_text, (20, y))

    status_text = needs_font.render(get_status(tama), True, (0, 0, 0))
    status_x = surface.get_width() - status_text.get_width() - 20
    surface.blit(status_text, (status_x, y))

def draw_below(surface, tama):
    global indicator_icon, needs_font
    if indicator_icon is None:
        indicator_icon, _ = load_image("sprite.png", None, 1)
        indicator_icon = pg.transform.scale(indicator_icon, (20, 20))
    if needs_font is None:
        needs_font = pg.font.Font(None, 30)

    icon_size = indicator_icon.get_width()
    gap = 20
    items = [tama.name, tama.plant_type]

    rendered = [needs_font.render(label, True, (0, 0, 0)) for label in items]
    item_widths = [icon_size + 4 + t.get_width() for t in rendered]
    total_width = sum(item_widths) + gap

    y = surface.get_height() - icon_size - 10
    start_x = (surface.get_width() - total_width) // 2

    for i, (text, item_width) in enumerate(zip(rendered, item_widths)):
        x = start_x + sum(item_widths[:i]) + i * gap
        surface.blit(indicator_icon, (x, y))
        surface.blit(text, (x + icon_size + 4, y))

class MenuScreen:
    def __init__(self, surface_width, surface_height):
        self.width = surface_width
        self.height = surface_height
        self.x = -surface_width
        self.target_x = -surface_width
        self.open = False
        self.speed = 20
        self.icon = None
        self.font = None
        self.selected = 0

        self.surface = pg.Surface((surface_width - 145, surface_height), pg.SRCALPHA)

    def toggle(self):
        self.open = not self.open
        self.target_x = 0 if self.open else -self.width

    def handle_key(self, key):
        if not self.open:
            return None
        items_count = 3
        if key in (pg.K_u, pg.K_l):
            self.selected = (self.selected - 1) % items_count
        elif key in (pg.K_d, pg.K_r):
            self.selected = (self.selected + 1) % items_count
        elif key == pg.K_y:
            return self.selected
        return None

    def update(self):
        if self.x < self.target_x:
            self.x = min(self.x + self.speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.speed, self.target_x)

    def draw(self, screen):
        if self.font is None:
            self.font = pg.font.Font(None, 30)
        if self.icon is None:
            icon_size = self.font.size("A")[1] * 2
            self.icon, _ = load_image("sprite.png", None, 1)
            self.icon = pg.transform.scale(self.icon, (icon_size, icon_size))

        if self.x >= -self.width:
            self.surface.fill((50, 50, 50, 255))

            items = ["Water", "Garden", "Journal"]
            icon_size = self.icon.get_width()
            text_height = self.font.size("A")[1]
            item_height = max(icon_size, text_height)
            item_gap = 16
            padding_left = 20

            total_height = len(items) * item_height + (len(items) - 1) * item_gap
            start_y = (self.surface.get_height() - total_height) // 2

            for i, item in enumerate(items):
                y = start_y + i * (item_height + item_gap)
                is_selected = i == self.selected

                icon_y = y + (item_height - icon_size) // 2

                if is_selected:
                    # bright: blit icon as-is
                    self.surface.blit(self.icon, (padding_left, icon_y))
                else:
                    # dim: blit icon then dark alpha overlay on top
                    dimmed = self.icon.copy()
                    dimmed.fill((150, 150, 150, 255), special_flags=pg.BLEND_RGBA_MULT)
                    self.surface.blit(dimmed, (padding_left, icon_y))

                color = (255, 255, 255) if is_selected else (100, 100, 100)
                text = self.font.render(item, True, color)
                text_y = y + (item_height - text_height) // 2
                self.surface.blit(text, (padding_left + icon_size + 10, text_y))

            screen.blit(self.surface, (self.x, 0))

class CareScreen:
    def __init__(self, surface_width, surface_height):
        self.width = surface_width
        self.height = surface_height
        self.x = surface_width  # slides in from the right
        self.target_x = surface_width
        self.open = False
        self.speed = 20
        self.font = None

        self.surface = pg.Surface((surface_width, surface_height))

    def show(self):
        self.open = True
        self.target_x = 0

    def hide(self):
        self.open = False
        self.target_x = self.width

    def handle_key(self, key):
        if key == pg.K_x:
            self.hide()

    def update(self):
        if self.x < self.target_x:
            self.x = min(self.x + self.speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.speed, self.target_x)

    def draw_content(self, surface, tama):
        pass  # overridden by subclasses

    def draw(self, screen, tama):
        if self.font is None:
            self.font = pg.font.Font(None, 30)

        if self.x < self.width:
            self.surface.fill((30, 30, 30))
            self.draw_content(self.surface, tama)
            screen.blit(self.surface, (self.x, 0))


class WaterScreen(CareScreen):
    def __init__(self, surface_width, surface_height):
        super().__init__(surface_width, surface_height)

    def draw_content(self, surface, tama):
        title = self.font.render("Water", True, (100, 200, 255))
        surface.blit(title, (20, 20))

        # thirst bar
        bar_w, bar_h = 200, 20
        x = (surface.get_width() - bar_w) // 2
        y = surface.get_height() // 2 - 10
        pg.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h))
        pg.draw.rect(surface, (100, 200, 255), (x, y, int(bar_w * tama.thirst / 100), bar_h))

        label = self.font.render(f"Water level: {int(tama.thirst)}%", True, (255, 255, 255))
        surface.blit(label, (x, y - 30))

        hint = self.font.render("Press Y to water", True, (150, 150, 150))
        surface.blit(hint, ((surface.get_width() - hint.get_width()) // 2, surface.get_height() - 40))

    def handle_key(self, key, tama):
        super().handle_key(key)
        if key == pg.K_y:
            tama.thirst = min(100, tama.thirst + 20)


class GardenScreen(CareScreen):
    def __init__(self, surface_width, surface_height):
        super().__init__(surface_width, surface_height)

    def draw_content(self, surface, tama):
        title = self.font.render("Garden", True, (100, 255, 150))
        surface.blit(title, (20, 20))

        bar_w, bar_h = 200, 20
        x = (surface.get_width() - bar_w) // 2
        y = surface.get_height() // 2 - 10
        pg.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h))
        pg.draw.rect(surface, (100, 255, 150), (x, y, int(bar_w * tama.vitality / 100), bar_h))

        label = self.font.render(f"Nutrients: {int(tama.vitality)}%", True, (255, 255, 255))
        surface.blit(label, (x, y - 30))

        hint = self.font.render("Fertilize(y)", True, (150, 150, 150))
        surface.blit(hint, ((surface.get_width() - hint.get_width()) // 2, surface.get_height() - 40))

    def handle_key(self, key, tama):
        super().handle_key(key)
        if key == pg.K_y:
            tama.vitality = min(100, tama.vitality + 20)


class JournalScreen(CareScreen):
    def __init__(self, surface_width, surface_height):
        super().__init__(surface_width, surface_height)
        self.entries = []

    def draw_content(self, surface, tama):
        title = self.font.render("Journal", True, (255, 200, 80))
        surface.blit(title, (20, 20))

        if not self.entries:
            msg = self.font.render("No entries yet.", True, (150, 150, 150))
            surface.blit(msg, (20, 60))
        else:
            for i, entry in enumerate(self.entries[-4:]):  # show last 4
                text = self.font.render(entry, True, (220, 220, 220))
                surface.blit(text, (20, 60 + i * 35))

        hint = self.font.render("Press Y to log entry", True, (150, 150, 150))
        surface.blit(hint, ((surface.get_width() - hint.get_width()) // 2, surface.get_height() - 40))

    def handle_key(self, key, tama):
        super().handle_key(key)
        if key == pg.K_y:
            from datetime import date
            self.entries.append(f"Day log: W{int(tama.thirst)} V{int(tama.vitality)} M{int(tama.mood)}")

# prepare game objects
tama = Tama()
allsprites = pg.sprite.RenderPlain(tama)

clock = pg.time.Clock()

menu = MenuScreen(screen.get_width(), screen.get_height())

care_screens = [
    WaterScreen(screen.get_width(), screen.get_height()),
    GardenScreen(screen.get_width(), screen.get_height()),
    JournalScreen(screen.get_width(), screen.get_height()),
]

active_care = None

# main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if active_care and active_care.open:
                active_care.handle_key(event.key, tama)
                if not active_care.open:
                    active_care = None
            elif event.key == pg.K_x:
                menu.toggle()
            else:
                selected = menu.handle_key(event.key)
                if selected is not None:
                    active_care = care_screens[selected]
                    active_care.show()
                    menu.toggle()
        if event.type == OPC_UPDATE:
            tama.opc_update(tama.water-25, tama.nutrients-25, tama.light-25, tama.age+1)

    allsprites.update()
    menu.update()
    if active_care:
        active_care.update()

    screen.fill("purple")
    #screen.blit(display, (0, 0))
    allsprites.draw(screen)
    draw_above(screen, tama)
    draw_needs(screen, tama)
    draw_below(screen, tama)
    menu.draw(screen)
    if active_care:
        active_care.draw(screen, tama)

    #pg.display.flip()
    raw = pg.image.tostring(screen, 'RGB')
    img = Image.frombytes('RGB', (320, 240), raw)
    disp.ShowImage(img)

    clock.tick(60)

pg.quit()