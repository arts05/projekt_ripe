"""Tegemist on Pythoni keskkonnas tehtud mänguga, mis on Pirogovi pargi 'Tower defense' (peamine menüü selleks mänguks). Autoriteks on Arthur Klettenberg ja Rene Miller
Kasutatud allikana on Tartu linna pilt Pirogovi pargist. Et mängida, pane käima main.py programm."""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import importlib

WIDTH, HEIGHT = 1260, 720
FPS = 60

def ensure_display():
    if not pygame.display.get_surface():
        pygame.display.set_mode((WIDTH, HEIGHT))
    return pygame.display.get_surface()

def run_menu(screen): #jooksutab menu.py, et kuvada menüü
    menu = importlib.import_module("menu")
    if hasattr(menu, "run_menu"):
        return menu.run_menu(screen)
    return "QUIT"

def run_game(screen): #jooksutab game.py, et alustada mängu
    try:
        game = importlib.import_module("game")
        if hasattr(game, "run_game"):
            return game.run_game(screen)
    except ModuleNotFoundError:
        pass

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q, pygame.K_BACKSPACE):
                return "BACK_TO_MENU"

        screen.fill((20, 20, 20))
        t1 = font.render("game.py puudub – placeholder.", True, (240, 240, 240))
        t2 = font.render("ESC / Q / Backspace = tagasi menüüsse", True, (200, 200, 200)) #oli esialgne placeholder
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 20))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        clock.tick(FPS)

def run_end(screen):
    end = importlib.import_module("end")
    if hasattr(end, "run_end"):
        return end.run_end(screen)
    return "QUIT"

def main(): #funktsioon, et kuvada ekraani ja teha vastavaid menüü vahetusi.
    pygame.init()
    pygame.display.set_caption("Piro survival")
    screen = ensure_display()
    clock = pygame.time.Clock()

    state = "MENU"
    running = True

    while running:
        clock.tick(FPS)

        if state == "MENU":
            result = run_menu(screen)
            if result == "START_GAME":
                state = "GAME"
            elif result == "QUIT":
                running = False

        elif state == "GAME":
            result = run_game(screen)
            if result == "BACK_TO_MENU":
                state = "MENU"
            elif result == "END_SCREEN":
                state = "END"
            elif result == "QUIT":
                running = False
        
        elif state == "END":
            result = run_end(screen)
            if result == "BACK_TO_MENU":
                state = "MENU"
            elif result == "QUIT":
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()
