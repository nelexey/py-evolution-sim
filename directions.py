from enum import Enum

class Direction(Enum):
    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

    @classmethod
    def from_genome_number(cls, number):
        return cls(number % 8)

    def get_offset(self):
        offsets = {
            Direction.NORTH: (0, -1),
            Direction.NORTHEAST: (1, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTHEAST: (1, 1),
            Direction.SOUTH: (0, 1),
            Direction.SOUTHWEST: (-1, 1),
            Direction.WEST: (-1, 0),
            Direction.NORTHWEST: (-1, -1)
        }
        return offsets[self]

    def left(self, steps=1):
        """Поворачивает влево на заданное количество шагов (45° за шаг)."""
        new_direction = (self.value - steps) % 8
        return Direction(new_direction)

    def right(self, steps=1):
        """Поворачивает вправо на заданное количество шагов (45° за шаг)."""
        new_direction = (self.value + steps) % 8
        return Direction(new_direction)
