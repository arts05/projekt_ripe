# menu.py
import os
import pygame
import pygame.freetype
from pygame.sprite import Sprite

WHITE = (255, 255, 255)
DARK_GREEN = (20, 60, 20)
DESCRIPTION_TEXT = (255, 255, 255)

GAME_DESCRIPTION = (
    "Tere tulemast!\n\n"
    "Sa oled julge tudeng enda sõpradega Pirogovi pargis reede õhtul.\n"
    "Kas sa suudad ennast kaitsta kohalike parmude eest ja ellu jääda?\n"
    "Vajuta 'Alusta', et enda elu pikimat reede õhtut kogeda."
)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb=None, bold=True):
    font = pygame.freetype.SysFont("Courier", int(font_size), bold=bold)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()

class UIElement(Sprite):
    def __init__(self, center_position, text, font_size, text_rgb, action=None):
        super().__init__()
        self.mouse_over = False
        self.action = action

        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=None
        )
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=None
        )

        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False
        return None

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class TextBox:
    def __init__(self, topleft, width, text, font_size, text_color, box_color, padding=12):
        self.topleft = topleft
        self.width = width
        self.text = text
        self.font = pygame.freetype.SysFont("Courier", int(font_size), bold=False)
        self.text_color = text_color
        self.box_color = box_color
        self.padding = padding

        self.lines = []
        self.line_height = self.font.get_sized_height()
        for raw_line in text.split("\n"):
            self.lines.extend(self._wrap_line(raw_line, width - 2 * padding))

        self.height = 2 * padding + len(self.lines) * self.line_height
        self.rect = pygame.Rect(topleft[0], topleft[1], width, self.height)

    def _wrap_line(self, line, max_width):
        words = line.split(" ")
        wrapped = []
        current = ""
        for word in words:
            test = word if current == "" else (current + " " + word)
            if self.font.get_rect(test).width <= max_width:
                current = test
            else:
                wrapped.append(current)
                current = word
        wrapped.append(current)
        return wrapped

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GREEN, self.rect, border_radius=8)
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding
        for line in self.lines:
            text_surface, _ = self.font.render(line, fgcolor=self.text_color)
            surface.blit(text_surface, (x, y))
            y += self.line_height

def run_menu(screen):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()

    bg_path = os.path.join(os.path.dirname(__file__), "assets", "piro.png")
    taust = pygame.image.load(bg_path).convert()
    taust = pygame.transform.scale(taust, (WIDTH, HEIGHT))

    desc_width = 900
    desc_x = (WIDTH - desc_width) // 2
    description_box = TextBox(
        topleft=(desc_x, 30),
        width=desc_width,
        text=GAME_DESCRIPTION,
        font_size=20,
        text_color=DESCRIPTION_TEXT,
        box_color=DARK_GREEN,
        padding=16,
    )

    start_btn = UIElement(
        center_position=(200, HEIGHT - 60),
        font_size=30,
        text_rgb=WHITE,
        text="Alusta",
        action="START_GAME",
    )
    quit_btn = UIElement(
        center_position=(WIDTH - 200, HEIGHT - 60),
        font_size=30,
        text_rgb=WHITE,
        text="Välju",
        action="QUIT",
    )

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True

        mouse_pos = pygame.mouse.get_pos()
        ui_action = start_btn.update(mouse_pos, mouse_up) or quit_btn.update(mouse_pos, mouse_up)
        if ui_action in ("START_GAME", "QUIT"):
            return ui_action

        screen.blit(taust, (0, 0))
        description_box.draw(screen)
        start_btn.draw(screen)
        quit_btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)
