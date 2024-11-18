import pygame
import random
from enum import Enum
from config import *
from directions import Direction


class CellType(Enum):
    PHOTOSYNTHETIC = 0
    PREDATOR = 1


class Cell:
    def __init__(self, block, genome=None, cell_type=CellType.PHOTOSYNTHETIC, clan_id=None):
        self.block = block
        self.block.cell = self
        self.genome = genome if genome else self._generate_genome(cell_type)
        self.energy = CELL_ENERGY_START
        self.max_energy = CELL_ENERGY_MAX
        self.age = 0
        self.direction = Direction.NORTH
        self.genome_step = 0
        self.cell_type = cell_type
        self.clan_id = clan_id if clan_id is not None else self._generate_clan_id()

        if cell_type == CellType.PHOTOSYNTHETIC:
            self.color = (0, 255, 0)  # Зеленый цвет
        else:
            self.color = (255, 0, 0)  # Красный цвет

    @staticmethod
    def _generate_clan_id():
        """Генерирует уникальный идентификатор клана для новых клеток."""
        return random.randint(1, 1000000)

    def _generate_genome(self, cell_type):
        if cell_type == CellType.PHOTOSYNTHETIC:
            return [random.randint(1, 64) for _ in range(64)]
        else:
            genome = [random.randint(1, 64) for _ in range(64)]
            # Заблокировать действие фотосинтеза для хищных клеток
            genome[25:33] = [0] * 8
            return genome

    def is_relative(self, other_cell):
        """Проверяет, является ли данная клетка родственником другой клетки."""
        return self.genome == other_cell.genome

    def draw(self, surface):
        center = (
            self.block.x * BLOCK_SIZE + BLOCK_SIZE // 2,
            self.block.y * BLOCK_SIZE + BLOCK_SIZE // 2
        )

        # Рисуем круг с полученным цветом
        # pygame.draw.circle(surface, self.color, center, BLOCK_SIZE // 2 - 1)
        # Рисуем квадрат с полученным цветом
        pygame.draw.rect(surface,
                         self.color,
                         pygame.Rect(center[0] - BLOCK_SIZE // 2,
                                     center[1] - BLOCK_SIZE // 2,
                                     BLOCK_SIZE - 1,
                                     BLOCK_SIZE - 1))

        # Рисуем направление
        direction_offset = self.direction.get_offset()
        end_point = (
            center[0] + direction_offset[0] * (BLOCK_SIZE // 3),
            center[1] + direction_offset[1] * (BLOCK_SIZE // 3)
        )
        pygame.draw.line(surface, (255, 255, 255), center, end_point, 2)

    def mutate_genome(self):
        new_genome = self.genome.copy()
        if random.random() < 0.125:
            mutation_point = random.randint(0, 63)
            new_genome[mutation_point] = random.randint(1, 64)

        return new_genome

    def process_action(self, world):
        """Обработка текущего действия клетки на основе текущего гена и его результата."""
        if self.energy <= 0 or self.age >= 1000 or (self.energy > self.max_energy and self.cell_type != CellType.PREDATOR):
            world.remove_cell(self)
            return

        current_gene = self.genome[self.genome_step]
        next_step = self._process_gene(current_gene, world)
        self.genome_step = (self.genome_step + next_step) % 64
        self.energy -= 1
        self.age += 1

    def _process_gene(self, gene, world):
        """Обработка текущего гена и выбор действия на основе диапазонов значений гена."""
        actions = {
            range(1, 9): self._look_forward,
            range(9, 17): self._move_forward,
            range(17, 25): self._turn,
            range(33, 41): self._reproduce,
        }

        if self.cell_type == CellType.PHOTOSYNTHETIC:
            actions.update({
                range(25, 33): self._photosynthesis,
                range(41, 49): self._give_energy,  # Новое действие для передачи энергии
            })
        else:
            actions.update({
                range(25, 33): self._attack,
                range(41, 49): self._steal_energy,  # Новое действие для воровства энергии
            })

        for number_range, action in actions.items():
            if gene in number_range:
                return action(world)

        return gene  # Если ген не соответствует ни одному действию

    def _look_forward(self, world, distance=1):
        """
        Определяет, что находится на указанном расстоянии впереди клетки.
        Аргументы:
            - distance (int): Расстояние, на котором клетка "смотрит" вперед.
        """
        x, y = self.block.get_coordinates()
        dx, dy = self.direction.get_offset()
        next_x, next_y = x + dx * distance, y + dy * distance

        if not world.is_valid_position(next_x, next_y):
            return 2  # Стена

        next_block = world.get_block(next_x, next_y)
        if next_block.is_empty():
            return 1  # Пустая клетка
        else:
            other_cell = next_block.cell
            if self.is_relative(other_cell):
                return 5  # Родственная клетка
            elif other_cell.cell_type == CellType.PHOTOSYNTHETIC:
                return 3  # Фотосинтетическая клетка
            else:
                return 4  # Хищная клетка

    def _move_forward(self, world):
        if self.energy < MOVEMENT_COST:
            return 1

        x, y = self.block.get_coordinates()
        dx, dy = self.direction.get_offset()
        next_x, next_y = x + dx, y + dy

        if world.is_valid_position(next_x, next_y) and world.get_block(next_x, next_y).is_empty():
            old_block = self.block
            new_block = world.get_block(next_x, next_y)
            old_block.cell = None
            self.block = new_block
            new_block.cell = self
            self.energy -= MOVEMENT_COST
            return 2
        return 1

    def _turn(self, world):
        # next_gene = self.genome[(self.genome_step + 1) % 64]
        # self.direction = Direction.from_genome_number(next_gene)
        # return 2

        next_gene = self.genome[(self.genome_step + 1) % 64]

        # Поворот на основе значения гена
        if 17 <= next_gene <= 20:
            # Повернуть влево на 90°
            self.direction = self.direction.left()
        elif 21 <= next_gene <= 24:
            # Повернуть вправо на 90°
            self.direction = self.direction.right()

        # Переход к следующему гену
        return 2

    def _photosynthesis(self, world):
        self.energy += PHOTOSYNTHESIS_ENERGY
        return 1

    def _reproduce(self, world):
        if self.energy < REPRODUCTION_THRESHOLD or (self.energy >= self.max_energy and self.cell_type == CellType.PHOTOSYNTHETIC):
            return 1

        x, y = self.block.get_coordinates()
        dx, dy = self.direction.get_offset()
        next_x, next_y = x + dx, y + dy

        if world.is_valid_position(next_x, next_y) and world.get_block(next_x, next_y).is_empty():
            new_genome = self.mutate_genome()
            new_block = world.get_block(next_x, next_y)

            # У потомка такой же клан, как у родителя
            new_cell = Cell(new_block, new_genome, self.cell_type, self.clan_id)

            world.cells.append(new_cell)  # Добавляем новую клетку в список мира

            # Разделяем энергию
            shared_energy = self.energy // 2
            self.energy = shared_energy
            new_cell.energy = shared_energy

            return 3
        return 1

    def _attack(self, world):
        x, y = self.block.get_coordinates()
        dx, dy = self.direction.get_offset()
        next_x, next_y = x + dx, y + dy

        if world.is_valid_position(next_x, next_y) and not world.get_block(next_x, next_y).is_empty():
            victim = world.get_block(next_x, next_y).cell
            if victim.clan_id != self.clan_id:
                self.energy += victim.energy
                world.remove_cell(victim)
                old_block = self.block
                new_block = world.get_block(next_x, next_y)
                old_block.cell = None
                self.block = new_block
                new_block.cell = self
                self.energy -= MOVEMENT_COST
                return 2
        return 1

    def _steal_energy(self, world):
        """Ворует часть энергии у клетки впереди, если это не родственник."""
        x, y = self.block.get_coordinates()
        dx, dy = self.direction.get_offset()
        next_x, next_y = x + dx, y + dy

        if world.is_valid_position(next_x, next_y) and not world.get_block(next_x, next_y).is_empty():
            target = world.get_block(next_x, next_y).cell

            # Проверка, является ли жертва родственником
            if self.is_relative(target):
                return 5  # Пропустить ход, если впереди родственник

            # Воровать энергию у неродственной клетки
            stolen_energy = target.energy * 0.2
            self.energy += stolen_energy
            target.energy -= target.energy * 0.4

            # Возвращаем разные значения в зависимости от типа клетки впереди
            if target.cell_type == CellType.PHOTOSYNTHETIC:
                return 3  # Фотосинтетическая клетка (не родственник)
            else:
                return 4  # Хищная клетка (не родственник)
        return 1  # Если впереди пусто или стена

    def _give_energy(self, world):
        """Передает часть энергии клетке впереди, если она существует и не заполнена энергией."""
        x, y = self.block.get_coordinates()
        dx, dy = self.direction.get_offset()
        next_x, next_y = x + dx, y + dy

        if world.is_valid_position(next_x, next_y) and not world.get_block(next_x, next_y).is_empty():
            target = world.get_block(next_x, next_y).cell

            # Передавать энергию только родственникам или фотосинтетическим клеткам
            if target.energy < target.max_energy:
                transferred_energy = self.energy * 0.2
                self.energy -= transferred_energy
                target.energy += transferred_energy

                # Различные значения в зависимости от типа клетки впереди
                if self.is_relative(target):
                    return 5  # Родственная клетка
                elif target.cell_type == CellType.PHOTOSYNTHETIC:
                    return 3  # Фотосинтетическая клетка
                else:
                    return 4  # Хищная клетка
        return 1  # Если впереди пусто или стена
