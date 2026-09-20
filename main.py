import pygame
from game import Game

def main():
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 600, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Barbie Glam Catch Game")
    clock = pygame.time.Clock()

    game = Game(screen, WIDTH, HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(pygame.key.get_pressed(), event)

        game.update()
        game.draw()

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()