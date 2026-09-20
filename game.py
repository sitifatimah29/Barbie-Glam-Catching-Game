import os
import pygame
import random
from pathlib import Path
from player import Player
from item import FallingItem

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)

        self.state = "MENU"

        bg_path = ASSETS_DIR / "images" / "background.png"
        if bg_path.exists():
            self.bg_image = pygame.image.load(str(bg_path))
            self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))
        else:
            self.bg_image = None

        sounds_dir = ASSETS_DIR / "sounds"
        bgm_file = next((f for f in sounds_dir.iterdir() if f.name.startswith("bgm")), None)
        catch_file = next((f for f in sounds_dir.iterdir() if f.name.startswith("catch")), None)
        wrong_file = next((f for f in sounds_dir.iterdir() if f.name.startswith("wrong")), None)

        if bgm_file:
            pygame.mixer.music.load(str(bgm_file))
            pygame.mixer.music.play(-1)

        self.sound_catch = pygame.mixer.Sound(str(catch_file)) if catch_file else None
        self.sound_wrong = pygame.mixer.Sound(str(wrong_file)) if wrong_file else None

        self.snowflakes = []
        for _ in range(40):
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x, y = random.randint(0, self.width), random.randint(0, 50)
            elif side == 'bottom':
                x, y = random.randint(0, self.width), random.randint(self.height - 50, self.height)
            elif side == 'left':
                x, y = random.randint(0, 50), random.randint(0, self.height)
            else:  # right
                x, y = random.randint(self.width - 50, self.width), random.randint(0, self.height)

            radius = random.randint(2, 5)
            self.snowflakes.append([x, y, radius])

        self.reset_game()

    def reset_game(self):
        self.player = Player(self.width, self.height)
        self.items = [FallingItem(self.width) for _ in range(3)]
        self.score = 0
        self.lives = 3
        self.timer_limit = 60
        self.timer = self.timer_limit
        self.start_ticks = pygame.time.get_ticks()
        self.freeze_active_until = 0

    def handle_input(self, keys, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "MENU" and event.key == pygame.K_RETURN:
                self.reset_game()
                self.state = "PLAYING"
            elif self.state == "PLAYING" and event.key == pygame.K_p:
                self.state = "PAUSED"
            elif self.state == "PAUSED" and event.key == pygame.K_p:
                self.state = "PLAYING"
            elif self.state == "GAMEOVER" and event.key == pygame.K_r:
                self.reset_game()
                self.state = "PLAYING"

    def update(self):
        if self.state != "PLAYING":
            return

        current_ticks = pygame.time.get_ticks()
        is_frozen = current_ticks < self.freeze_active_until

        seconds_passed = (current_ticks - self.start_ticks) // 1000
        time_remaining = self.timer_limit - seconds_passed
        self.timer = max(0, time_remaining)

        if self.timer <= 0 or self.lives <= 0:
            self.state = "GAMEOVER"
            return

        speed_multiplier = 1.0 + (self.score // 50) * 0.15

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        for item in self.items:
            item.update(speed_multiplier, is_frozen)

            if self.player.rect.colliderect(item.rect):
                if item.type == "bomb":
                    if self.sound_wrong:
                        self.sound_wrong.play()
                    self.lives += item.lives_change
                elif item.type == "freeze":
                    if self.sound_catch:
                        self.sound_catch.play()
                    self.score += item.points
                    self.freeze_active_until = current_ticks + 5000
                else:
                    if self.sound_catch:
                        self.sound_catch.play()
                    self.score += item.points
                    if item.time_change > 0:
                        self.start_ticks += item.time_change * 1000

                item.reset()

            if item.rect.top > self.height:
                item.reset()

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 40))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill((255, 181, 204))

        if self.state == "MENU":
            menu_bg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            menu_bg.fill((0, 0, 0, 100))
            self.screen.blit(menu_bg, (0, 0))

            txt = self.title_font.render("BARBIE GLAM MAKEOVER", True, (255, 105, 180))
            sub = self.font.render("Press [ENTER] To Start", True, (255, 255, 255))
            self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, 120))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, 220))

        elif self.state in ["PLAYING", "PAUSED"]:
            self.player.draw(self.screen)
            for item in self.items:
                item.draw(self.screen)

            hud_score = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            hud_lives_label = self.font.render("Lives: ", True, (255, 255, 255))
            hud_lives_hearts = self.font.render("♥" * max(0, self.lives), True, (255, 50, 50))
            hud_time = self.font.render(f"Time: {self.timer}s", True, (255, 255, 255))

            hud_surface = pygame.Surface((self.width, 90), pygame.SRCALPHA)
            pygame.draw.rect(hud_surface, (0, 0, 0, 140), (10, 5, 170, 75), border_radius=10)
            pygame.draw.rect(hud_surface, (0, 0, 0, 140), (self.width - 165, 5, 155, 45), border_radius=10)
            self.screen.blit(hud_surface, (0, 0))

            self.screen.blit(hud_score, (20, 10))
            self.screen.blit(hud_lives_label, (20, 45))
            self.screen.blit(hud_lives_hearts, (20 + hud_lives_label.get_width(), 45))
            self.screen.blit(hud_time, (self.width - 150, 12))

            if pygame.time.get_ticks() < self.freeze_active_until:
                pygame.draw.rect(self.screen, (173, 216, 230), (0, 0, self.width, self.height), 8)
                pygame.draw.rect(self.screen, (240, 248, 255), (8, 8, self.width - 16, self.height - 16), 3)

                for flake in self.snowflakes:
                    x, y, radius = flake
                    pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius)
                    pygame.draw.circle(self.screen, (135, 206, 250), (x, y), radius + 1, 1)

            if self.state == "PAUSED":
                pause_box = pygame.Rect(self.width // 2 - 180, 170, 360, 60)
                pygame.draw.rect(self.screen, (0, 0, 0), pause_box, border_radius=10)
                pause_txt = self.title_font.render("PAUSED (Press 'P')", True, (255, 0, 0))
                self.screen.blit(pause_txt, (self.width // 2 - pause_txt.get_width() // 2, 175))

        elif self.state == "GAMEOVER":
            go_bg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            go_bg.fill((0, 0, 0, 120))
            self.screen.blit(go_bg, (0, 0))

            txt = self.title_font.render("GAME OVER", True, (255, 50, 50))
            sc = self.font.render(f"Accumulated Points: {self.score}", True, (255, 255, 255))
            res = self.font.render("Press [R] To Start Again", True, (255, 105, 180))
            self.screen.blit(txt, (self.width // 2 - txt.get_width() // 2, 100))
            self.screen.blit(sc, (self.width // 2 - sc.get_width() // 2, 180))
            self.screen.blit(res, (self.width // 2 - res.get_width() // 2, 240))