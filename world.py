from block import Block
from cell import Cell, CellType
from config import *
import random

class World:
    def __init__(self):
        self.width = WINDOW_WIDTH // BLOCK_SIZE
        self.height = WINDOW_HEIGHT // BLOCK_SIZE
        self.blocks = [[Block(x, y) for y in range(self.height)] for x in range(self.width)]
        self.cells = []

    def add_cell(self, x, y, cell_type=CellType.PHOTOSYNTHETIC):
        if self.is_valid_position(x, y) and self.get_block(x, y).is_empty():
            cell = Cell(self.get_block(x, y), cell_type=cell_type)
            self.cells.append(cell)
            return cell
        return None

    def update(self):
        # Копируем список, чтобы избежать проблем при изменении списка во время итерации
        cells_to_update = self.cells.copy()
        for cell in cells_to_update:
            if cell.energy <= 0:
                self.remove_cell(cell)
                continue
            cell.process_action(self)

    def remove_cell(self, cell):
        if cell in self.cells:
            cell.block.cell = None
            self.cells.remove(cell)

    def draw(self, surface):
        surface.fill((0, 0, 0))
        for row in self.blocks:
            for block in row:
                block.draw(surface)

    def get_block(self, x, y):
        if self.is_valid_position(x, y):
            return self.blocks[x][y]
        return None

    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height