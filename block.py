import pygame
from config import *


class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cell = None
        self.rect = pygame.Rect(
            x * BLOCK_SIZE,
            y * BLOCK_SIZE,
            BLOCK_SIZE,
            BLOCK_SIZE
        )

    def draw(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.rect, 1)
        if self.cell:
            self.cell.draw(surface)

    def get_coordinates(self):
        return (self.x, self.y)

    def is_empty(self):
        return self.cell is None