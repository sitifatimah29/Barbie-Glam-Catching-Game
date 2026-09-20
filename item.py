import os
import pygame
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class FallingItem:
    TYPES = {
        "lipstick": {"points": 10, "lives": 0, "time": 0, "speed": 4},
        "crown": {"points": 50, "lives": 0, "time": 0, "speed": 6},
        "perfume": {"points": 10, "lives": 0, "time": 3, "speed": 5},
        "bomb": {"points": 0, "lives": -1, "time": 0, "speed": 7},
        "freeze": {"points": 5, "lives": 0, "time": 0, "speed": 5}  # Item Freeze
    }

    item_deck = []

    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.rect = None
        self.reset()

    def _get_next_type(self):
        if not FallingItem.item_deck:
            FallingItem.item_deck = ["lipstick", "crown", "perfume", "bomb", "freeze"]
            random.shuffle(FallingItem.item_deck)

        return FallingItem.item_deck.pop()

    def reset(self):
        self.type = self._get_next_type()

        info = self.TYPES[self.type]
        self.points = info["points"]
        self.lives_change = info["lives"]
        self.time_change = info["time"]
        self.speed = info["speed"]

        img_path = os.path.join(BASE_DIR, "assets", "images", f"{self.type}.png")
        self.image = pygame.image.load(img_path)
        self.image = pygame.transform.scale(self.image, (45, 45))

        if self.rect is None:
            self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, self.screen_width - self.rect.width)
        self.rect.y = random.randint(-100, -40)

    def update(self, speed_multiplier=1.0, is_frozen=False):
        current_speed = self.speed * speed_multiplier

        if is_frozen:
            current_speed *= 0.5

        self.rect.y += max(1, int(current_speed))

    def draw(self, screen):
        screen.blit(self.image, self.rect)