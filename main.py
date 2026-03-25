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

import os, math, random
import pygame as pg

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

    if image.get_masks()[3]:  # has alpha channel
        image = image.convert_alpha()
    else:
        image = image.convert()
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
pg.init()
# screen = pg.display.set_mode((800, 480), pg.FULLSCREEN | pg.NOFRAME)
screen = pg.display.set_mode((800, 480))

SW = screen.get_width()
SH = screen.get_height()

# globals
needs_font = None
needs_icon = None
status_icon = None
indicator_icon = None
scale = SW / 160

# opc update
OPC_UPDATE = pg.USEREVENT + 1 # checks for OPC update every 10 minutes
pg.time.set_timer(OPC_UPDATE, 2000)  # 600,000 ms = 10 minutes

# create the display
display = pg.Surface(screen.get_size())
display = display.convert()

bg =  pg.image.load(os.path.join(img_dir, "bg.png"))
bg = bg.convert()

# os.path.join(img_dir, "bg.png"

class Tama(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image("tama.png", None, .13*scale)
        self.rect.midleft = (int(SW * 0.06), display.get_rect().centery-20)

        self.thirst = 100
        self.vitality = 100
        self.mood = 100
        self.age = 0

        self.name = "Sprout"
        self.plant_type = "Fern"

    def opc_update(self, water, nutrients, light, age):
        self.thirst = water / WATER_MAX * 100
        self.vitality = nutrients / NUTR_MAX * 100
        self.mood = light / LIGHT_MAX * 100
        self.age = int(age)

    def status_update(self):
        # all 3 low
        if self.thirst < 25 and self.vitality < 25 and self.mood < 25:
            self.update_sprite("tama_wilt")
        # minimum low
        elif min(self.thirst, self.vitality, self.mood) < 50:
            lowest = min(
                (self.thirst, "thirst"),
                (self.vitality, "vitality"),
                (self.mood, "mood")
            )[1]

            if lowest == "thirst":
                self.update_sprite("tama_wilt")
            elif lowest == "vitality":
                self.update_sprite("tama_wilt")
            elif lowest == "mood":
                self.update_sprite("tama_wilt")
        # else, make happy
        else:
            self.update_sprite("tama")


    def update_sprite(self, img):
        self.image, self.rect = load_image(img+".png", None, .13 * scale)
        self.rect.midleft = (int(SW * 0.06), display.get_rect().centery - 20)

def get_font(size_ratio):
    """Return a font sized relative to screen height."""
    return pg.font.Font(None, max(8, int(SH * size_ratio)))

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

    font_size_ratio = 0.125         # ~30px at 240h
    bar_width  = int(SW * 0.31)     # ~100px at 320w
    bar_height = int(SH * 0.083)    # ~20px at 240h
    padding    = int(SH * 0.125)    # ~30px at 240h
    margin_x   = int(SW * 0.0625)   # ~20px at 320w
    start_y    = int(SH * 0.229)    # ~55px at 240h
    icon_dim   = int(SH * 0.067)    # small icon square

    if needs_font is None:
        needs_font = get_font(font_size_ratio)
    if needs_icon is None:
        needs_icon, _ = load_image("sprite.png", None, 1)
        needs_icon = pg.transform.scale(needs_icon, (icon_dim, icon_dim))

    x = surface.get_width() - bar_width - margin_x

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
        label_y = y + bar_height + 2
        surface.blit(needs_icon, (x, label_y))
        remaining_x = x + icon_dim + int(SW * 0.0125)
        remaining_width = bar_width - icon_dim - int(SW * 0.0125)
        text_x = remaining_x + (remaining_width - text.get_width()) // 2
        surface.blit(text, (text_x, label_y))

def draw_above(surface, tama):
    global status_icon, needs_font

    font_size_ratio = 0.125
    icon_dim  = int(SH * 0.067)
    margin_x  = int(SW * 0.0625)
    margin_y  = int(SH * 0.042)

    if status_icon is None:
        status_icon, _ = load_image("sprite.png", None, 1)
        status_icon = pg.transform.scale(status_icon, (icon_dim, icon_dim))
    if needs_font is None:
        needs_font = get_font(font_size_ratio)

    day_text = needs_font.render(f"Day {tama.age}", True, (0, 0, 0))
    surface.blit(day_text, (margin_x, margin_y))

    status_text = needs_font.render(get_status(tama), True, (0, 0, 0))
    status_x = surface.get_width() - status_text.get_width() - margin_x
    surface.blit(status_text, (status_x, margin_y))

def draw_below(surface, tama):
    global indicator_icon, needs_font

    font_size_ratio = 0.125
    icon_dim = int(SW * 0.0625)   # ~20px at 320w
    gap      = int(SW * 0.0625)   # ~20px at 320w
    margin_b = int(SH * 0.042)    # ~10px at 240h

    if indicator_icon is None:
        indicator_icon, _ = load_image("sprite.png", None, 1)
        indicator_icon = pg.transform.scale(indicator_icon, (icon_dim, icon_dim))
    if needs_font is None:
        needs_font = get_font(font_size_ratio)

    items = [tama.name, tama.plant_type]
    rendered = [needs_font.render(label, True, (0, 0, 0)) for label in items]
    item_widths = [icon_dim + int(SW * 0.0125) + t.get_width() for t in rendered]
    total_width = sum(item_widths) + gap

    y = surface.get_height() - icon_dim - margin_b
    start_x = (surface.get_width() - total_width) // 2

    for i, (text, item_width) in enumerate(zip(rendered, item_widths)):
        x = start_x + sum(item_widths[:i]) + i * gap
        surface.blit(indicator_icon, (x, y))
        surface.blit(text, (x + icon_dim + int(SW * 0.0125), y))

class MenuScreen:
    def __init__(self, surface_width, surface_height):
        self.width = surface_width
        self.height = surface_height
        self.x = -surface_width
        self.target_x = -surface_width
        self.open = False
        self.speed = int(surface_width * 0.0625)  # ~20px at 320w
        self.icon = None
        self.font = None
        self.selected = 0

        panel_width = surface_width - int(surface_width * 0.453)  # leaves ~145px gap at 320w
        self.surface = pg.Surface((panel_width, surface_height), pg.SRCALPHA)
        self._panel_width = panel_width

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
            self.font = get_font(0.125)
        if self.icon is None:
            icon_dim = int(self.font.size("A")[1] * 2)
            self.icon, _ = load_image("sprite.png", None, 1)
            self.icon = pg.transform.scale(self.icon, (icon_dim, icon_dim))

        if self.x >= -self.width:
            self.surface.fill((50, 50, 50, 255))

            items = ["Water", "Garden", "Journal"]
            icon_size   = self.icon.get_width()
            text_height = self.font.size("A")[1]
            item_height = max(icon_size, text_height)
            item_gap    = int(SH * 0.067)   # ~16px at 240h
            padding_left = int(self._panel_width * 0.125)  # proportional left pad

            total_height = len(items) * item_height + (len(items) - 1) * item_gap
            start_y = (self.surface.get_height() - total_height) // 2

            for i, item in enumerate(items):
                y = start_y + i * (item_height + item_gap)
                is_selected = i == self.selected
                icon_y = y + (item_height - icon_size) // 2

                if is_selected:
                    self.surface.blit(self.icon, (padding_left, icon_y))
                else:
                    dimmed = self.icon.copy()
                    dimmed.fill((150, 150, 150, 255), special_flags=pg.BLEND_RGBA_MULT)
                    self.surface.blit(dimmed, (padding_left, icon_y))

                color = (255, 255, 255) if is_selected else (100, 100, 100)
                text = self.font.render(item, True, color)
                text_y = y + (item_height - text_height) // 2
                self.surface.blit(text, (padding_left + icon_size + int(SW * 0.03), text_y))

            screen.blit(self.surface, (self.x, 0))

class CareScreen:
    def __init__(self, surface_width, surface_height):
        self.width = surface_width
        self.height = surface_height
        self.x = surface_width
        self.target_x = surface_width
        self.open = False
        self.speed = int(surface_width * 0.0625)  # ~20px at 320w
        self.font = None

        self.surface = pg.Surface((surface_width, surface_height))

    def show(self):
        self.open = True
        self.target_x = 0

    def hide(self):
        self.open = False
        self.target_x = self.width

    def handle_key(self, key, tama):
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
            self.font = get_font(0.125)

        if self.x < self.width:
            self.surface.fill((30, 30, 30))
            self.draw_content(self.surface, tama)
            screen.blit(self.surface, (self.x, 0))

class WaterScreen(CareScreen):
    def __init__(self, surface_width, surface_height):
        super().__init__(surface_width, surface_height)

    def draw_content(self, surface, tama):
        w, h = surface.get_size()
        bar_w = int(w * 0.625)   # ~200px at 320w
        bar_h = int(h * 0.083)   # ~20px at 240h
        margin_x = int(w * 0.0625)
        margin_y = int(h * 0.083)
        hint_pad = int(h * 0.167)  # ~40px at 240h

        title = self.font.render("Water", True, (100, 200, 255))
        surface.blit(title, (margin_x, margin_y))

        x = (w - bar_w) // 2
        y = h // 2 - bar_h // 2
        pg.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h))
        pg.draw.rect(surface, (100, 200, 255), (x, y, int(bar_w * tama.thirst / 100), bar_h))

        label = self.font.render(f"Water level: {int(tama.thirst)}%", True, (255, 255, 255))
        surface.blit(label, (x, y - int(h * 0.125)))

        hint = self.font.render("Press Y to water", True, (150, 150, 150))
        surface.blit(hint, ((w - hint.get_width()) // 2, h - hint_pad))

    def handle_key(self, key, tama):
        super().handle_key(key, tama)
        if key == pg.K_y:
            tama.thirst = min(100, tama.thirst + 20)

class GardenScreen(CareScreen):
    def __init__(self, surface_width, surface_height):
        super().__init__(surface_width, surface_height)

    def draw_content(self, surface, tama):
        w, h = surface.get_size()
        bar_w = int(w * 0.625)
        bar_h = int(h * 0.083)
        margin_x = int(w * 0.0625)
        margin_y = int(h * 0.083)
        hint_pad = int(h * 0.167)

        title = self.font.render("Garden", True, (100, 255, 150))
        surface.blit(title, (margin_x, margin_y))

        x = (w - bar_w) // 2
        y = h // 2 - bar_h // 2
        pg.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h))
        pg.draw.rect(surface, (100, 255, 150), (x, y, int(bar_w * tama.vitality / 100), bar_h))

        label = self.font.render(f"Nutrients: {int(tama.vitality)}%", True, (255, 255, 255))
        surface.blit(label, (x, y - int(h * 0.125)))

        hint = self.font.render("Fertilize(y)", True, (150, 150, 150))
        surface.blit(hint, ((w - hint.get_width()) // 2, h - hint_pad))

    def handle_key(self, key, tama):
        super().handle_key(key, tama)
        if key == pg.K_y:
            tama.vitality = min(100, tama.vitality + 20)

class JournalScreen(CareScreen):
    def __init__(self, surface_width, surface_height):
        super().__init__(surface_width, surface_height)
        self.entries = []

    def draw_content(self, surface, tama):
        w, h = surface.get_size()
        margin_x = int(w * 0.0625)
        margin_y = int(h * 0.083)
        entry_gap = int(h * 0.146)   # ~35px at 240h
        hint_pad  = int(h * 0.167)

        title = self.font.render("Journal", True, (255, 200, 80))
        surface.blit(title, (margin_x, margin_y))

        if not self.entries:
            msg = self.font.render("No entries yet.", True, (150, 150, 150))
            surface.blit(msg, (margin_x, margin_y + int(h * 0.125)))
        else:
            for i, entry in enumerate(self.entries[-4:]):
                text = self.font.render(entry, True, (220, 220, 220))
                surface.blit(text, (margin_x, margin_y + int(h * 0.125) + i * entry_gap))

        hint = self.font.render("Press Y to log entry", True, (150, 150, 150))
        surface.blit(hint, ((w - hint.get_width()) // 2, h - hint_pad))

    def handle_key(self, key, tama):
        super().handle_key(key, tama)
        if key == pg.K_y:
            from datetime import date
            self.entries.append(f"Day log: W{int(tama.thirst)} V{int(tama.vitality)} M{int(tama.mood)}")

# prepare game objects
tama = Tama()
allsprites = pg.sprite.RenderPlain(tama)

clock = pg.time.Clock()

menu = MenuScreen(SW, SH)

care_screens = [
    WaterScreen(SW, SH),
    GardenScreen(SW, SH),
    JournalScreen(SW, SH),
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
            tama.opc_update(tama.thirst - random.randint(0,25), tama.vitality - random.randint(0,25), tama.mood - random.randint(0,25), tama.age + 1)
            tama.status_update()

    allsprites.update()
    menu.update()
    if active_care:
        active_care.update()

    screen.fill([255, 255, 255])
    screen.blit(bg, (0, 0))

    allsprites.draw(screen)
    draw_above(screen, tama)
    draw_needs(screen, tama)
    draw_below(screen, tama)
    menu.draw(screen)
    if active_care:
        active_care.draw(screen, tama)

    pg.display.flip()

    clock.tick(60)

pg.quit()