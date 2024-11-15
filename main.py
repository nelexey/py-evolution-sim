import pygame
import random
from world import World
from cell import CellType
from config import *


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    world = World()

    # Создаем начальные фотосинтезирующие клетки
    for _ in range(2000):
        x = random.randint(0, world.width - 1)
        y = random.randint(0, world.height - 1)
        world.add_cell(x, y)

    # Создаем начальных хищников
    for _ in range(400):
        x = random.randint(0, world.width - 1)
        y = random.randint(0, world.height - 1)
        world.add_cell(x, y, CellType.PREDATOR)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Добавление новых клеток по клику
                pos = pygame.mouse.get_pos()
                x, y = pos[0] // BLOCK_SIZE, pos[1] // BLOCK_SIZE
                if random.random() < 0.5:
                    world.add_cell(x, y)
                else:
                    world.add_cell(x, y, CellType.PREDATOR)

        world.update()
        world.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()