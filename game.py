"""Tegemist on Pythoni keskkonnas tehtud mänguga, mis on Pirogovi pargi 'Tower defense'. Autoriteks on Arthur Klettenberg ja Rene Miller
Eeskujuna kastuatud allikad on Tartu linna poolt tehtud pildid Pirogovi pargist ning Maa- ja Ruumiameti sateliitpildid"""

import os
import math
import random
import pygame
import glob  # (ENEMY_PATTERN tugi)

# ---- VÄRVID / KONSTANDID ----
WHITE  = (255, 255, 255)
RED    = (220, 60, 60)
GREEN  = (40, 160, 60)
YELLOW = (250, 220, 70)
BLACK  = (10,  10,  10)
DARK_GREEN = (20, 60, 20)

# Taustapildi failinimi (asub kaustas assets/) – jätame samaks stiiliks nagu sul oli
BG_FILENAME = os.path.join(os.path.dirname(__file__), "assets", "pirogov_droon.png")

# Sprite-failide täisteed (nagu soovisid)
PLAYER_LOOK   = os.path.join(os.path.dirname(__file__), "assets", "tekkelpixel.png")
ENEMY_PATTERN = os.path.join(os.path.dirname(__file__), "assets", "parm*.png")  # (ENEMY_PATTERN tugi)

# Mängija algpositsioon (suhtelised koordinaadid ekraani mõõtude suhtes)
SPAWN_REL = (0.535, 0.305)

# Suurused (ringide/“hitboxi” raadiused px)
PLAYER_R = 18
ENEMY_R  = 14


# ---- ABIFUNKTSIOONID ----
def _unit_vec(ax, ay, bx, by):
    """Ühikuvektor punktist (ax, ay) punkti (bx, by) suunas."""
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    if d == 0:
        return 0.0, 0.0
    return dx / d, dy / d


def _load_enemy_sprites(pattern, diameter):
    """(ENEMY_PATTERN) Lae kõik vastase sprited mustriga pattern, skaleeri hitboxi mõõtu ja joonda keskmesse."""
    sprites = []
    for path in sorted(glob.glob(pattern)):
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            continue
        w, h = img.get_width(), img.get_height()
        scale = diameter / max(w, h)
        img = pygame.transform.smoothscale(img, (max(1, int(w*scale)), max(1, int(h*scale))))
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        surf.blit(img, img.get_rect(center=(diameter//2, diameter//2)))
        sprites.append(surf)
    return sprites

# Lae 1x kõik variandid mällu (globaalne list) – (ENEMY_PATTERN)
ENEMY_SPRITES = _load_enemy_sprites(ENEMY_PATTERN, diameter=ENEMY_R*2)


def _asset_path(name):
    """Koosta täistee assets-kausta alla (nagu sinu varasem stiil)."""
    return os.path.join(os.path.dirname(__file__), "assets", name)


def _load_background(w, h):
    """Laeb taustapildi assets-kaustast ja skaleerib akna (w,h) mõõtu."""
    img = pygame.image.load(_asset_path(BG_FILENAME)).convert()
    return pygame.transform.scale(img, (w, h))


def _load_sprite_or_none_from_path(path, diameter):
    """
    Laeb PNG antud TÄISTEELT ja skaleerib proportsionaalselt nii, et max(mõõdud) = diameter.
    Tagastab Surface, mis on läbipaistva taustaga ruut (diameter x diameter),
    kuhu pilt on keskele paigutatud. Kui faili pole või tekib viga, tagastab None.
    """
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
    except Exception:
        return None

    w, h = img.get_width(), img.get_height()
    scale = diameter / max(w, h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    img = pygame.transform.smoothscale(img, (new_w, new_h))

    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    rect = img.get_rect(center=(diameter // 2, diameter // 2))
    surf.blit(img, rect)
    return surf


# ---- KLASSID ----
class Player:
    """Mängija – paikneb pildil, ei liigu; saab tulistada hiire suunas."""

    def __init__(self, x, y, sprite=None):
        self.pos = pygame.Vector2(x, y)  # asukoht ekraanil
        self.r = PLAYER_R                # ringi raadius joonistamiseks / tabamuseks
        self.hp = 3                      # elud
        self.cooldown = 0.15             # tulistamise vahe (sekundites)
        self._cd = 0.0                   # sisemine taimer cooldowni jaoks
        self.sprite = sprite             # eel-skaleeritud Surface või None

    def update(self, dt):
        """Uuenda cooldowni taimerit."""
        if self._cd > 0:
            self._cd -= dt

    def can_shoot(self):
        """Kas võib tulistada (cooldown läbi)?"""
        return self._cd <= 0

    def shoot(self, tx, ty):
        """Loo uus kuul, mis liigub mängija asukohast hiirekoha suunas."""
        self._cd = self.cooldown
        dx, dy = _unit_vec(self.pos.x, self.pos.y, tx, ty)
        return Bullet(self.pos.x, self.pos.y, dx, dy)

    def draw(self, s):
        """Joonista mängija (sprite või ring) ja väike sihikujoon hiire suunas."""
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            s.blit(self.sprite, rect)
        else:
            pygame.draw.circle(s, GREEN, (int(self.pos.x), int(self.pos.y)), self.r)

        # sihikujoon
        mx, my = pygame.mouse.get_pos()
        dx, dy = _unit_vec(self.pos.x, self.pos.y, mx, my)
        tip = (int(self.pos.x + dx * self.r), int(self.pos.y + dy * self.r))
        pygame.draw.line(s, WHITE, self.pos, tip, 2)


class Bullet:
    """Kuul – liigub sirgjooneliselt antud suunas ja kaob pärast teatud aega või ekraanilt lahkudes."""

    def __init__(self, x, y, dx, dy):
        self.pos = pygame.Vector2(x, y)         # asukoht
        self.vel = pygame.Vector2(dx, dy) * 600 # kiirus (px/s)
        self.r = 4
        self.alive = True
        self.life = 2.0                         # eluiga sekundites

    def update(self, dt, w, h):
        """Liiguta kuuli ja kontrolli eluiga/raame."""
        self.pos += self.vel * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False
        # Kui lahkub ekraanilt liiga kaugele, kustuta
        if self.pos.x < -50 or self.pos.x > w + 50 or self.pos.y < -50 or self.pos.y > h + 50:
            self.alive = False

    def draw(self, s):
        """Joonista kuul."""
        pygame.draw.circle(s, YELLOW, (int(self.pos.x), int(self.pos.y)), self.r)


class Enemy:
    """Vaenlane – sünnib ekraani servast ja liigub otse mängija poole."""

    def __init__(self, wave, w, h, sprite=None):
        # Vali juhuslik serv, kuhu spawnida
        side = random.choice(("t", "b", "l", "r"))
        if side == "t":
            self.pos = pygame.Vector2(random.randint(0, w), -20)
        if side == "b":
            self.pos = pygame.Vector2(random.randint(0, w), h + 20)
        if side == "l":
            self.pos = pygame.Vector2(-20, random.randint(0, h))
        if side == "r":
            self.pos = pygame.Vector2(w + 20, random.randint(0, h))

        # Kiirus kasvab laine numbriga veidi
        base = 70 + wave * 4
        self.speed = random.uniform(base * 0.9, base * 1.2)

        self.r = ENEMY_R
        self.hp = 1 + (1 if wave >= 6 else 0)  # alates 6. lainest veidi sitkem
        self.alive = True

        # (ENEMY_PATTERN) vali juhuslik baassprite varamust (võib olla tühi list → None)
        self.sprite_base = random.choice(ENEMY_SPRITES) if ENEMY_SPRITES else None

    def update(self, dt, target_pos):
        """Liigu sihtmärgi (mängija) suunas."""
        dx, dy = _unit_vec(self.pos.x, self.pos.y, target_pos.x, target_pos.y)
        self.pos.x += dx * self.speed * dt
        self.pos.y += dy * self.speed * dt

    def hit(self, dmg=1):
        """Võta pihta – kui HP ≤ 0, sure."""
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, s, target_pos):
        """(ENEMY_PATTERN) Joonista vaenlane – sprite pööratud mängija suunas või ring."""
        if self.sprite_base:
            dx = target_pos.x - self.pos.x
            dy = target_pos.y - self.pos.y
            angle_deg = -math.degrees(math.atan2(dy, dx))  # ekraani Y kasvab alla
            img = pygame.transform.rotozoom(self.sprite_base, angle_deg, 1.0)
            rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            s.blit(img, rect)
        else:
            pygame.draw.circle(s, RED, (int(self.pos.x), int(self.pos.y)), self.r)


class Waves:
    """Lainehaldur – hoiab mitut lainet, spawni tempot ja liikumist järgmisele lainele."""

    def __init__(self):
        self.wave = 1
        self.max_wave = 10
        self.spawned = 0
        self.to_spawn = self._count(self.wave)  # mitu vaenlast selles laines kokku
        self.interval = 0.6                     # spawnimise vahe (s)
        self.acc = 0.0
        self.done_spawning = False              # kas kõik vaenlased on selles laines välja lastud

    def _count(self, w):
        """Tagasta antud laine vaenlaste kogus."""
        return 5 + (w - 1) * 3

    def update(self, dt, enemies, W, H, enemy_sprite):
        """Lisa vaenlasi ajapõhiselt, kuni kogus täis."""
        if self.done_spawning:
            return
        self.acc += dt
        while self.acc >= self.interval and self.spawned < self.to_spawn:
            self.acc -= self.interval
            # Enemy valib ise juhusliku skin'i ENEMY_SPRITES listist; 'enemy_sprite' arg jäetakse alles, kuid ei kasutata
            enemies.append(Enemy(self.wave, W, H, sprite=enemy_sprite))
            self.spawned += 1
        if self.spawned >= self.to_spawn:
            self.done_spawning = True

    def try_next(self, enemies):
        """Kui selles laines enam vaenlasi pole, liigu järgmisele; 10. järel võit."""
        if self.done_spawning and not enemies:
            if self.wave >= self.max_wave:
                return "win"
            self.wave += 1
            self.spawned = 0
            self.to_spawn = self._count(self.wave)
            self.done_spawning = False
        return None


# ---- PÕHIFUNKTSIOON, MIDA main.py KUTSUB ----
def run_game(screen):
    """Käivita mängusilmus. Tagasta 'QUIT' või 'BACK_TO_MENU'."""
    clock = pygame.time.Clock()
    W, H = screen.get_size()

    # Lae ja skaleeri taust; arvuta mängija algpositsioon ekraani mõõtudes
    bg_image = _load_background(W, H)

    # Lae ja skaleeri sprited (kui puuduvad, tagastab None → joonistame ringid)
    player_sprite = _load_sprite_or_none_from_path(PLAYER_LOOK, diameter=PLAYER_R * 2)
    enemy_sprite  = _load_sprite_or_none_from_path(ENEMY_PATTERN,  diameter=ENEMY_R  * 2)  # (jääb alles; Enemy ei kasuta)

    spawn_x = int(SPAWN_REL[0] * W)
    spawn_y = int(SPAWN_REL[1] * H)

    # Mängu olek
    player = Player(spawn_x, spawn_y, sprite=player_sprite)
    bullets, enemies = [], []
    waves = Waves()
    score = 0

    state = "play"                       # "play" | "win" | "lose"
    font = pygame.font.SysFont("consolas", 22)
    font_big = pygame.font.SysFont("consolas", 28, bold=True)

    while True:
        dt = clock.tick(60) / 1000.0     # kaadri aeg sekundites

        # SISENDID
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "BACK_TO_MENU"
            if state == "play":
                # Vasak hiireklõps – tulistamine hiire suunas (kui cooldown lubab)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.can_shoot():
                    mx, my = pygame.mouse.get_pos()
                    bullets.append(player.shoot(mx, my))
            else:
                # Võidu/kaotuse ekraanilt ükskõik milline klahv → menüüsse
                if event.type == pygame.KEYDOWN:
                    return "BACK_TO_MENU"

        # Kui pole mänguseisund "play", joonista lõpp-ekraan ja oota klahvi
        if state != "play":
            # Kasutame sama mängu taustapilti ka lõppseisus (eraldiseisvat lõputausta ei kasutata)
            screen.blit(bg_image, (0, 0))

            if state == "win":
                # ülemine lint + sõnum
                banner_h = 60
                pygame.draw.rect(screen, DARK_GREEN, (0, 0, W, banner_h))
                msg = "Palju õnne! Sa jäid ellu ja saad minna edasi Shooters'isse!"
                text = font_big.render(msg, True, WHITE)
                screen.blit(text, (W // 2 - text.get_width() // 2, (banner_h - text.get_height()) // 2))
            else:
                # kaotuse lühitekst keskel
                t1 = font_big.render("KAOTUS! HP sai otsa.", True, WHITE)
                screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 20))

            # all rida juhiseks
            t2 = font.render("Vajuta suvalist klahvi – tagasi menüüsse", True, WHITE)
            screen.blit(t2, (W // 2 - t2.get_width() // 2, H - 40))
            pygame.display.flip()
            continue

        # ---- LOOGIKA ----
        player.update(dt)
        waves.update(dt, enemies, W, H, enemy_sprite)

        # Kuulid edasi ja prügikoristus
        for b in bullets:
            b.update(dt, W, H)
        bullets = [b for b in bullets if b.alive]

        # Vaenlased liiguvad mängija suunas
        for e in enemies:
            e.update(dt, player.pos)

        # Kuulide ja vaenlaste tabamused
        for e in enemies:
            if not e.alive:
                continue
            for b in bullets:
                if not b.alive:
                    continue
                if (e.pos - b.pos).length() <= e.r + b.r:
                    e.hit(1)
                    b.alive = False
                    if not e.alive:
                        score += 10
        enemies = [e for e in enemies if e.alive]

        # Vaenlane jõuab mängijani → mängija kaotab 1 HP, vaenlane hävineb
        for e in enemies:
            if (e.pos - player.pos).length() <= e.r + player.r:
                player.hp -= 1
                e.alive = False
        enemies = [e for e in enemies if e.alive]

        # Kaotus kui HP otsas
        if player.hp <= 0:
            state = "lose"

        # Kui laine läbi (kõik vaenlased hävitatud), liigu järgmisele; pärast 10. võit
        res = waves.try_next(enemies)
        if res == "win":
            state = "win"

        # ---- JOONISTAMINE ----
        screen.blit(bg_image, (0, 0))    # taustakaart
        for b in bullets:
            b.draw(screen)
        for e in enemies:
            e.draw(screen, player.pos)   # (ENEMY_PATTERN) pööramine mängija suunas
        player.draw(screen)

        # HUD (ülakõrvale)
        hud = [
            f"Laine: {waves.wave}/10",
            f"HP: {player.hp}",
            f"Skoor: {score}",
            f"Vaenlasi: {len(enemies)}",
        ]
        for i, line in enumerate(hud):
            t = font.render(line, True, WHITE)
            screen.blit(t, (10, 10 + i * 24))

        pygame.display.flip()
