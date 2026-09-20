import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Player:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        img_path = os.path.join(BASE_DIR, "assets", "images", "player.png")
        self.image = pygame.image.load(img_path)
        self.image = pygame.transform.scale(self.image, (100, 80))

        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 10
        self.speed = 8

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < self.screen_width:
            self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)