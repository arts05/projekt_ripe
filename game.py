import os
import math
import random
import pygame

WHITE  = (255, 255, 255)
RED    = (220, 60, 60)
GREEN  = (40, 160, 60)
YELLOW = (250, 220, 70)
BLACK  = (10, 10, 10)

BG_FILENAME = os.path.join(os.path.dirname(__file__), "assets", "pirogov_droon.png")
SPAWN_REL = (0.535, 0.305)
def _unit_vec(ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    d = math.hypot(dx, dy)
    if d == 0: return 0.0, 0.0
    return dx/d, dy/d

def _load_background(w, h):
    base_dir = os.path.dirname(__file__)
    bg_path = os.path.join(base_dir, "assets", BG_FILENAME)
    img = pygame.image.load(bg_path).convert()
    return pygame.transform.scale(img, (w, h))

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.r = 18
        self.hp = 3
        self.cooldown = 0.15
        self._cd = 0.0
    def update(self, dt):
        if self._cd > 0: self._cd -= dt
    def can_shoot(self): return self._cd <= 0
    def shoot(self, tx, ty):
        self._cd = self.cooldown
        dx, dy = _unit_vec(self.pos.x, self.pos.y, tx, ty)
        return Bullet(self.pos.x, self.pos.y, dx, dy)
    def draw(self, s):
        pygame.draw.circle(s, GREEN, (int(self.pos.x), int(self.pos.y)), self.r)
        mx, my = pygame.mouse.get_pos()
        dx, dy = _unit_vec(self.pos.x, self.pos.y, mx, my)
        tip = (int(self.pos.x + dx*self.r), int(self.pos.y + dy*self.r))
        pygame.draw.line(s, WHITE, self.pos, tip, 2)

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(dx, dy) * 600
        self.r = 4
        self.alive = True
        self.life = 2.0
    def update(self, dt, w, h):
        self.pos += self.vel * dt
        self.life -= dt
        if self.life <= 0: self.alive = False
        if self.pos.x < -50 or self.pos.x > w+50 or self.pos.y < -50 or self.pos.y > h+50:
            self.alive = False
    def draw(self, s):
        pygame.draw.circle(s, YELLOW, (int(self.pos.x), int(self.pos.y)), self.r)

class Enemy:
    def __init__(self, wave, w, h):
        side = random.choice(("t","b","l","r"))
        if side=="t": self.pos = pygame.Vector2(random.randint(0,w), -20)
        if side=="b": self.pos = pygame.Vector2(random.randint(0,w), h+20)
        if side=="l": self.pos = pygame.Vector2(-20, random.randint(0,h))
        if side=="r": self.pos = pygame.Vector2(w+20, random.randint(0,h))
        base = 70 + wave*4
        self.speed = random.uniform(base*0.9, base*1.2)
        self.r = 14
        self.hp = 1 + (1 if wave >= 6 else 0)
        self.alive = True
    def update(self, dt, target_pos):
        dx, dy = _unit_vec(self.pos.x, self.pos.y, target_pos.x, target_pos.y)
        self.pos.x += dx * self.speed * dt
        self.pos.y += dy * self.speed * dt
    def hit(self, dmg=1):
        self.hp -= dmg
        if self.hp <= 0: self.alive = False
    def draw(self, s):
        pygame.draw.circle(s, RED, (int(self.pos.x), int(self.pos.y)), self.r)

class Waves:
    def __init__(self):
        self.wave = 1
        self.max_wave = 10
        self.spawned = 0
        self.to_spawn = self._count(self.wave)
        self.interval = 0.6
        self.acc = 0.0
        self.done_spawning = False
    def _count(self, w): return 5 + (w-1)*3
    def update(self, dt, enemies, W, H):
        if self.done_spawning: return
        self.acc += dt
        while self.acc >= self.interval and self.spawned < self.to_spawn:
            self.acc -= self.interval
            enemies.append(Enemy(self.wave, W, H))
            self.spawned += 1
        if self.spawned >= self.to_spawn:
            self.done_spawning = True
    def try_next(self, enemies):
        if self.done_spawning and not enemies:
            if self.wave >= self.max_wave: return "win"
            self.wave += 1
            self.spawned = 0
            self.to_spawn = self._count(self.wave)
            self.done_spawning = False
        return None

def run_game(screen):
    clock = pygame.time.Clock()
    W, H = screen.get_size()

    bg_image = _load_background(W, H)
    spawn_x = int(SPAWN_REL[0] * W)
    spawn_y = int(SPAWN_REL[1] * H)

    player = Player(spawn_x, spawn_y)
    bullets, enemies = [], []
    waves = Waves()
    score = 0

    state = "play"
    font = pygame.font.SysFont("consolas", 22)

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            if state == "play":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.can_shoot():
                    mx, my = pygame.mouse.get_pos()
                    bullets.append(player.shoot(mx, my))
            else:
                if event.type == pygame.KEYDOWN:
                    return "BACK_TO_MENU"

        if state != "play":
            screen.blit(bg_image, (0, 0))
            msg = "VÕIT! 10 lainet puhastatud." if state == "win" else "KAOTUS! HP sai otsa."
            t1 = font.render(msg, True, WHITE)
            t2 = font.render("Vajuta suvalist klahvi – tagasi menüüsse", True, WHITE)
            screen.blit(t1, (W//2 - t1.get_width()//2, H//2 - 20))
            screen.blit(t2, (W//2 - t2.get_width()//2, H//2 + 18))
            pygame.display.flip()
            continue

        player.update(dt)
        waves.update(dt, enemies, W, H)

        for b in bullets: b.update(dt, W, H)
        bullets = [b for b in bullets if b.alive]

        for e in enemies: e.update(dt, player.pos)

        for e in enemies:
            if not e.alive: continue
            for b in bullets:
                if not b.alive: continue
                if (e.pos - b.pos).length() <= e.r + b.r:
                    e.hit(1); b.alive = False
                    if not e.alive: score += 10
        enemies = [e for e in enemies if e.alive]

        for e in enemies:
            if (e.pos - player.pos).length() <= e.r + player.r:
                player.hp -= 1
                e.alive = False
        enemies = [e for e in enemies if e.alive]
        if player.hp <= 0:
            state = "lose"

        res = waves.try_next(enemies)
        if res == "win":
            state = "win"

        screen.blit(bg_image, (0, 0))
        for b in bullets: b.draw(screen)
        for e in enemies: e.draw(screen)
        player.draw(screen)

        hud = [
            f"Laine: {waves.wave}/10",
            f"HP: {player.hp}",
            f"Skoor: {score}",
            f"Vaenlasi: {len(enemies)}",
        ]
        for i, line in enumerate(hud):
            t = font.render(line, True, WHITE)
            screen.blit(t, (10, 10 + i*24))

        pygame.display.flip()
