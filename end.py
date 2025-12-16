import os
import pygame

WHITE = (255, 255, 255)

TEKST = (
    "Palju õnne! Sa jäid ellu ja saad minna edasi Shooters'isse!\n"
    "\n"
    "Vajuta suvalist klahvi, et naasta menüüsse."
)

def _render_multiline_center(surface, font, text, color, center_x, center_y, line_gap=6):
    """
    Joonista mitmerealine tekst nii, et kogu tekstiploki keskpunkt on (center_x, center_y).
    Tagastab joonistatud ploki alumise serva y-koordinaadi.
    """
    lines = text.split("\n")
    rendered = [font.render(line, True, color) for line in lines]
    heights = [surf.get_height() for surf in rendered]
    total_h = sum(heights) + line_gap * (len(rendered) - 1)
    start_y = int(center_y - total_h // 2)

    y = start_y
    for surf in rendered:
        x = int(center_x - surf.get_width() // 2)
        surface.blit(surf, (x, y))
        y += surf.get_height() + line_gap
    return y

def run_end(screen):
    clock = pygame.time.Clock()
    W, H = screen.get_size()

    # Taustapilt
    bg_path = os.path.join(os.path.dirname(__file__), "assets", "päike.png")
    bg = pygame.image.load(bg_path).convert()
    bg = pygame.transform.scale(bg, (W, H))

    # Fondid
    font_big = pygame.font.SysFont("Courier", 40, bold=True)
    font = pygame.font.SysFont("Courier", 22, bold=True)

    title_text = "VÕIT!"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                return "BACK_TO_MENU"

        screen.blit(bg, (0, 0))

        # Pealkiri (keskele, veidi kõrgemale)
        title_surf = font_big.render(title_text, True, WHITE)
        title_x = W // 2 - title_surf.get_width() // 2
        title_y = H // 2 - 100
        screen.blit(title_surf, (title_x, title_y))

        # Mitmerealne teade (keskele)
        _render_multiline_center(
            screen, font, TEKST, WHITE,
            center_x=W // 2,
            center_y=H // 2 + 20,
            line_gap=6
        )

        pygame.display.flip()
        clock.tick(60)
