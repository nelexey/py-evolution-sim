import pygame
import random
from world import World
from cell import CellType
from config import *
from settings_ui import ControlPanel


def main():
    pygame.init()

    # Создаем окно фиксированного размера
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Создаем панель управления
    control_panel = ControlPanel(width=200)

    # Создаем игровой мир с правильными размерами (без смещения)
    game_width = WINDOW_WIDTH - control_panel.width
    world = World(width=game_width // BLOCK_SIZE, height=WINDOW_HEIGHT // BLOCK_SIZE)

    # Создаем начальные клетки с учетом новой ширины
    for _ in range(2000):
        x = random.randint(0, world.width - 1)
        y = random.randint(0, world.height - 1)
        world.add_cell(x, y)

    for _ in range(400):
        x = random.randint(0, world.width - 1)
        y = random.randint(0, world.height - 1)
        world.add_cell(x, y, CellType.PREDATOR)

    frame_counter = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Проверяем, не попал ли клик на панель управления
                if mouse_pos[0] > control_panel.width:
                    # Пересчитываем координаты относительно игрового поля
                    game_x = (mouse_pos[0] - control_panel.width) // BLOCK_SIZE
                    game_y = mouse_pos[1] // BLOCK_SIZE
                    if 0 <= game_x < world.width and 0 <= game_y < world.height:
                        if random.random() < 0.5:
                            world.add_cell(game_x, game_y)
                        else:
                            world.add_cell(game_x, game_y, CellType.PREDATOR)
                else:
                    # Обработка кликов по панели управления
                    control_panel.handle_event(event)
            else:
                control_panel.handle_event(event)

        # Обновление мира с учетом frame_skip
        frame_counter += 1
        if frame_counter >= control_panel.frame_skip:
            world.update()
            frame_counter = 0

        # Обновление статистики
        control_panel.update_stats(world)

        # Очистка экрана
        screen.fill((0, 0, 0))

        # Создаем подповерхность для игрового мира
        game_surface = screen.subsurface(pygame.Rect(
            control_panel.width, 0,
            WINDOW_WIDTH - control_panel.width, WINDOW_HEIGHT
        ))

        # Отрисовка мира и панели управления
        world.draw(game_surface, control_panel)
        control_panel.draw(screen)

        pygame.display.flip()
        clock.tick(control_panel.fps)

    pygame.quit()


if __name__ == "__main__":
    main()