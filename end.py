import os
import pygame

WHITE = (255, 255, 255)

def run_end(screen):
    clock = pygame.time.Clock()
    W, H = screen.get_size()

    bg_path = os.path.join(os.path.dirname(__file__), "assets", "päike.png")
    bg = pygame.image.load(bg_path).convert()
    bg = pygame.transform.scale(bg, (W, H))

    font_big = pygame.font.SysFont("consolas", 36, bold=True)
    font = pygame.font.SysFont("consolas", 22)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                return "BACK_TO_MENU"

        screen.blit(bg, (0, 0))

        title = font_big.render("VÕIT!", True, WHITE)
        info = font.render(
            "Palju õnne! Sa jäid ellu ja saad minna edasi Shooters'isse!\n\nVajuta suvalist klahvi, et naasta menüüsse.",
            True,
            WHITE,
        )

        screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 40))
        screen.blit(info, (W // 2 - info.get_width() // 2, H // 2 + 10))

        pygame.display.flip()
        clock.tick(60)
