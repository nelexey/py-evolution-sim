import pygame
from enum import Enum
import colorsys

from config import *


class DisplayMode(Enum):
    TYPES = 'Types'
    ENERGY = 'Energy'
    CLANS = 'Clans'


class ControlPanel:
    def __init__(self, width=200):
        self.width = width
        self.font = pygame.font.Font(None, 24)
        self.display_mode = DisplayMode.TYPES
        self.fps = FPS
        self.frame_skip = 0

        # Цвета
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.button_color = (60, 60, 60)
        self.button_hover_color = (80, 80, 80)
        self.active_button_color = (100, 100, 100)

        # Отступы и размеры
        self.padding = 10
        self.button_height = 30
        self.section_margin = 20

        # Кнопки и элементы управления
        self.buttons = {}
        self.labels = {}
        self._create_controls()

        # Кэш цветов для кланов
        self.clan_colors = {}

        # Статистика
        self.stats = {
            'total_cells': 0,
            'photosynthetic': 0,
            'predators': 0
        }

    def _create_controls(self):
        y = self.padding

        # Секция FPS
        self.labels['fps'] = {'text': 'FPS Control', 'pos': (self.padding, y)}
        y += 25

        self.buttons['fps_down'] = pygame.Rect(self.padding, y, 30, self.button_height)
        self.buttons['fps_value'] = pygame.Rect(45, y, 70, self.button_height)
        self.buttons['fps_up'] = pygame.Rect(120, y, 30, self.button_height)

        y += self.button_height + self.section_margin

        # Секция Frame Skip
        self.labels['skip'] = {'text': 'Frame Skip', 'pos': (self.padding, y)}
        y += 25

        self.buttons['skip_down'] = pygame.Rect(self.padding, y, 30, self.button_height)
        self.buttons['skip_value'] = pygame.Rect(45, y, 70, self.button_height)
        self.buttons['skip_up'] = pygame.Rect(120, y, 30, self.button_height)

        y += self.button_height + self.section_margin

        # Секция Display Mode
        self.labels['mode'] = {'text': 'Display Mode', 'pos': (self.padding, y)}
        y += 25

        button_width = (self.width - 2 * self.padding - 20) // 3
        for i, mode in enumerate(DisplayMode):
            self.buttons[f'mode_{mode.name}'] = pygame.Rect(
                self.padding + i * (button_width + 10),
                y,
                button_width,
                self.button_height
            )

        y += self.button_height + self.section_margin

        # Секция статистики
        self.labels['stats'] = {'text': 'Statistics', 'pos': (self.padding, y)}
        y += 25
        self.labels['total'] = {'text': 'Total: 0', 'pos': (self.padding, y)}
        y += 20
        self.labels['photo'] = {'text': 'Plant: 0', 'pos': (self.padding, y)}
        y += 20
        self.labels['pred'] = {'text': 'Predator: 0', 'pos': (self.padding, y)}

    def get_game_rect(self, screen_height):
        """Возвращает прямоугольник для игрового поля"""
        return pygame.Rect(self.width, 0, screen_height, screen_height)

    def get_clan_color(self, clan_id):
        if clan_id not in self.clan_colors:
            hue = (clan_id * 0.618033988749895) % 1
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.95)
            self.clan_colors[clan_id] = tuple(int(x * 255) for x in rgb)
        return self.clan_colors[clan_id]

    def get_cell_color(self, cell):
        if self.display_mode == DisplayMode.TYPES:
            return cell.color
        elif self.display_mode == DisplayMode.ENERGY:
            normalized_energy = min(max(cell.energy / cell.max_energy, 0), 1)
            if normalized_energy <= 0.5:
                r = g = 255 * (normalized_energy * 2)
                b = 0
            else:
                r = g = 255
                b = 255 * ((normalized_energy - 0.5) * 2)
            return (int(r), int(g), int(b))
        else:  # DisplayMode.CLANS
            return self.get_clan_color(cell.clan_id)

    def update_stats(self, world):
        """Обновляет статистику мира"""
        self.stats['total_cells'] = len(world.cells)
        self.stats['photosynthetic'] = sum(1 for cell in world.cells if cell.cell_type.name == 'PHOTOSYNTHETIC')
        self.stats['predators'] = sum(1 for cell in world.cells if cell.cell_type.name == 'PREDATOR')

        # Обновляем текст статистики
        self.labels['total']['text'] = f'Total: {self.stats["total_cells"]}'
        self.labels['photo']['text'] = f'Plant: {self.stats["photosynthetic"]}'
        self.labels['pred']['text'] = f'Predator: {self.stats["predators"]}'

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # FPS controls
            if self.buttons['fps_down'].collidepoint(mouse_pos):
                self.fps = max(1, self.fps - 10)
                return True
            elif self.buttons['fps_up'].collidepoint(mouse_pos):
                self.fps = min(240, self.fps + 10)
                return True

            # Frame skip controls
            elif self.buttons['skip_down'].collidepoint(mouse_pos):
                self.frame_skip = max(1, self.frame_skip - 1)
                return True
            elif self.buttons['skip_up'].collidepoint(mouse_pos):
                self.frame_skip = min(10, self.frame_skip + 1)
                return True

            # Display mode controls
            for mode in DisplayMode:
                if self.buttons[f'mode_{mode.name}'].collidepoint(mouse_pos):
                    self.display_mode = mode
                    return True

        return False

    def draw(self, surface):
        # Фон панели управления
        pygame.draw.rect(surface, self.bg_color, (0, 0, self.width, surface.get_height()))
        pygame.draw.line(surface, (50, 50, 50), (self.width - 1, 0),
                         (self.width - 1, surface.get_height()), 2)

        # Отрисовка заголовков секций
        for label_info in self.labels.values():
            text = self.font.render(label_info['text'], True, self.text_color)
            surface.blit(text, label_info['pos'])

        # FPS controls
        pygame.draw.rect(surface, self.button_color, self.buttons['fps_down'])
        pygame.draw.rect(surface, self.button_color, self.buttons['fps_up'])
        pygame.draw.rect(surface, self.button_color, self.buttons['fps_value'])

        # Текст для FPS
        fps_text = self.font.render(str(self.fps), True, self.text_color)
        fps_rect = fps_text.get_rect(center=self.buttons['fps_value'].center)
        surface.blit(fps_text, fps_rect)

        # Символы + и -
        minus = self.font.render("-", True, self.text_color)
        plus = self.font.render("+", True, self.text_color)
        surface.blit(minus, minus.get_rect(center=self.buttons['fps_down'].center))
        surface.blit(plus, plus.get_rect(center=self.buttons['fps_up'].center))

        # Frame skip controls
        pygame.draw.rect(surface, self.button_color, self.buttons['skip_down'])
        pygame.draw.rect(surface, self.button_color, self.buttons['skip_up'])
        pygame.draw.rect(surface, self.button_color, self.buttons['skip_value'])

        # Текст для Frame Skip
        skip_text = self.font.render(str(self.frame_skip), True, self.text_color)
        skip_rect = skip_text.get_rect(center=self.buttons['skip_value'].center)
        surface.blit(skip_text, skip_rect)

        surface.blit(minus, minus.get_rect(center=self.buttons['skip_down'].center))
        surface.blit(plus, plus.get_rect(center=self.buttons['skip_up'].center))

        # Display mode buttons
        for mode in DisplayMode:
            button = self.buttons[f'mode_{mode.name}']
            color = self.active_button_color if self.display_mode == mode else self.button_color
            pygame.draw.rect(surface, color, button)

            mode_text = self.font.render(mode.value, True, self.text_color)
            text_rect = mode_text.get_rect(center=button.center)
            surface.blit(mode_text, text_rect)