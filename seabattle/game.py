# coding: utf-8

from __future__ import unicode_literals

import random
import re
import logging
import math
from itertools import product, chain

from transliterate import translit

EMPTY = 0
SHIP = 1
BLOCKED = 2
HIT = 3
MISS = 4
SKIP = 5


LAYOUT_VERTICAL = 1
LAYOUT_HORIZONTAL = 2
LAYOUT_UNKNOWN = -1

log = logging.getLogger(__name__)


class BaseGame(object):
    position_patterns = [re.compile('^([a-zа-я]+)(\d+)$', re.UNICODE),  # a1
                         re.compile('^([a-zа-я]+)\s+(\w+)$', re.UNICODE),  # a 1; a один
                         re.compile('^(\w+)\s+(\w+)$', re.UNICODE),  # a 1; a один; 7 10
                         ]

    str_letters = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к']
    str_numbers = ['один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять']

    letters_mapping = {
        'the': 'з',
        'за': 'з',
        'уже': 'ж',
        'трень': '3',
    }

    default_ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

    def __init__(self):
        self.size = 0
        self.ships = None
        self.field = []
        self.enemy_field = []

        self.ships_count = 0
        self.enemy_ships_count = 0

        self.last_shot_position = None
        self.last_shot_damage = None
        self.last_enemy_shot_position = None
        self.next_shot_index = None
        self.numbers = None

    def start_new_game(self, size=10, field=None, ships=None, numbers=None):
        assert(size <= 10)
        assert(len(field) == size ** 2 if field is not None else True)

        self.size = size
        self.numbers = numbers if numbers is not None else False

        if ships is None:
            self.ships = self.default_ships
        else:
            self.ships = ships

        if field is None:
            self.generate_field()
        else:
            self.field = field

        self.enemy_field = [EMPTY] * self.size ** 2

        self.ships_count = self.enemy_ships_count = len(self.ships)

        self.last_shot_position = None
        self.last_enemy_shot_position = None

    def generate_field(self):
        raise NotImplementedError()

    def print_field(self, field=None):
        if not self.size:
            log.info('Empty field')
            return

        if field is None:
            field = self.field

        mapping = ['.', '1', '.', 'X', 'x', 'x']

        lines = ['']
        lines.append('-' * (self.size + 2))
        for y in range(self.size):
            lines.append('|%s|' % ''.join(str(mapping[x]) for x in field[y * self.size: (y + 1) * self.size]))
        lines.append('-' * (self.size + 2))
        log.info('\n'.join(lines))

    def print_enemy_field(self):
        self.print_field(self.enemy_field)

    def handle_enemy_shot(self, position):
        index = self.calc_index(position)

        if self.field[index] == SHIP:
            self.field[index] = HIT

            if self.is_dead_ship(index):
                self.ships_count -= 1
                return 'kill'
            else:
                return 'hit'
        elif self.field[index] == HIT:
            return 'kill' if self.is_dead_ship(index) else 'hit'
        else:
            return 'miss'

    def is_dead_ship(self, last_index):
        x, y = self.calc_position(last_index)
        x -= 1
        y -= 1

        def _line_is_dead(line, index):
            def _tail_is_dead(tail):
                for i in tail:
                    if i == HIT:
                        continue
                    elif i == SHIP:
                        return False
                    else:
                        return True
                return True

            return _tail_is_dead(line[index:]) and _tail_is_dead(line[index::-1])

        return (
            _line_is_dead(self.field[x::self.size], y) and
            _line_is_dead(self.field[y * self.size:(y + 1) * self.size], x)
        )

    def is_end_game(self):
        return self.is_victory() or self.is_defeat()

    def is_victory(self):
        return self.enemy_ships_count < 1

    def is_defeat(self):
        return self.ships_count < 1

    def do_shot(self):
        raise NotImplementedError()

    def after_enemy_ship_killed(self):
        pass

    def after_enemy_ship_damaged(self):
        pass

    def after_our_miss(self):
        pass

    def repeat(self):
        return self.convert_from_position(self.last_shot_position, numbers=True)

    def reset_last_shot(self):
        self.last_shot_position = None

    def handle_enemy_reply(self, message):
        if self.last_shot_position is None:
            return

        index = self.calc_index(self.last_shot_position)

        if message in ['hit', 'kill']:
            self.enemy_field[index] = SHIP

            if message == 'kill':
                self.after_enemy_ship_killed()
                self.enemy_ships_count -= 1

            if message == 'hit':
                self.after_enemy_ship_damaged()
        elif message == 'miss':
            self.enemy_field[index] = MISS
            self.after_our_miss()

        self.print_enemy_field()

    def calc_index(self, position):
        x, y = position

        print(x, y)

        if x > self.size or y > self.size:
            raise ValueError('Wrong position: %s %s' % (x, y))

        return (y - 1) * self.size + x - 1

    def calc_position(self, index):
        y = index / self.size + 1
        x = index % self.size + 1

        return x, y

    def convert_to_position(self, position):
        position = position.lower()
        for pattern in self.position_patterns:
            match = pattern.match(position)

            if match is not None:
                break
        else:
            raise ValueError('Can\'t parse entire position: %s' % position)

        bits = match.groups()

        def _try_letter(bit):
            # проверяем особые случаи неправильного распознования STT
            bit = self.letters_mapping.get(bit, bit)

            # преобразуем в кириллицу
            bit = translit(bit, 'ru')

            try:
                return self.str_letters.index(bit) + 1
            except ValueError:
                raise

        def _try_number(bit):
            # проверяем особые случаи неправильного распознования STT
            bit = self.letters_mapping.get(bit, bit)

            if bit.isdigit():
                return int(bit)
            else:
                try:
                    return self.str_numbers.index(bit) + 1
                except ValueError:
                    raise

        x = bits[0].strip()
        try:
            x = _try_number(x)
        except ValueError:
            raise ValueError('Can\'t parse X point: %s' % x)

        y = bits[1].strip()
        try:
            y = _try_number(y)
        except ValueError:
            raise ValueError('Can\'t parse Y point: %s' % y)

        return x, y

    def convert_from_position(self, position, numbers=None):
        numbers = numbers if numbers is not None else self.numbers

        if numbers:
            x = position[0]
        else:
            x = self.str_letters[position[0] - 1]

        y = position[1]

        return '%s, %s' % (x, y)


class Game(BaseGame):
    def generate_field(self):
        self.field = [0] * self.size ** 2

        for length in self.ships:
            self.place_ship(length)

        for i in range(len(self.field)):
            if self.field[i] == BLOCKED:
                self.field[i] = EMPTY

    def place_ship(self, length):
        def _try_to_place():
            x = random.randint(1, self.size)
            y = random.randint(1, self.size)
            direction = random.choice([1, self.size])

            index = self.calc_index((x, y))
            values = self.field[index:None if direction == self.size else index + self.size - index % self.size:direction][:length]

            if len(values) < length or any(values):
                return False

            for i in range(length):
                current_index = index + direction * i

                for j in [0, 1, -1]:
                    if (j != 0
                            and current_index % self.size in (0, self.size - 1)
                            and (current_index + j) % self.size in (0, self.size - 1)):
                        continue

                    for k in [0, self.size, -self.size]:
                        neighbour_index = current_index + k + j

                        if (neighbour_index < 0
                                or neighbour_index >= len(self.field)
                                or self.field[neighbour_index] == SHIP):
                            continue

                        self.field[neighbour_index] = BLOCKED

                self.field[current_index] = SHIP

            return True

        while not _try_to_place():
            pass

    def is_point_invalid(self, p):
        return p[0] <= 0 or p[1] <= 0 or p[0] > self.size or p[1] > self.size

    def nearest_generator(self, pos):
        """
        Generate cells positions around current.
        """
        off_temp = (-1, 0, 1)

        for off_x, off_y in product(off_temp, off_temp):
            if not off_x and not off_y:
                continue
            n_x, n_y = pos[0] + off_x, pos[1] + off_y
            if self.is_point_invalid((n_x, n_y)):
                continue
            yield n_x, n_y

    def disable_for_shot_all_near(self):
        def check_cell_for_skip(pos):
            c = self.enemy_field[self.calc_index(pos)]
            if c == EMPTY:
                self.enemy_field[self.calc_index(pos)] = SKIP
                return EMPTY
            elif c == SHIP:
                return SHIP

        ship_checked_cells = set()
        next_checks = set()

        next_checks.add(self.last_shot_position)

        while True:
            try:
                ship_cell = next_checks.pop()
                if ship_cell in ship_checked_cells:
                    continue
            except KeyError:
                break

            ship_checked_cells.add(ship_cell)

            for pos in self.nearest_generator(ship_cell):
                if check_cell_for_skip(pos) == SHIP:
                    next_checks.add(pos)

    def generate_lines(self, i, c):
        def get_pos(ni):
            if c == 0:
                return ni, i
            else:
                return i, ni

        def get_field(ni):
            return self.enemy_field[self.calc_index(get_pos(ni))]

        si = 0
        line_start = None

        while si <= self.size:
            si += 1

            if si <= self.size and get_field(si) == EMPTY and line_start is None:
                line_start = si
                continue

            if si > self.size or get_field(si) != EMPTY:
                if line_start is None:
                    continue

                line_end = si - 1

                if line_start == line_end:
                    mi = line_start
                else:
                    d = int(math.floor((line_end - line_start) / 2.0))
                    mi = line_end - d

                yield get_pos(mi), (line_end - line_start + 1)

                line_start = None

    def generate_horizontal_lines_points(self):
        for i in range(1, self.size + 1):
            for r in self.generate_lines(i, 0):
                yield r

    def generate_vertical_lines_points(self):
        for i in range(1, self.size + 1):
            for r in self.generate_lines(i, 1):
                yield r

    def get_random_filtered_point(self):
        all_points = list(chain(self.generate_horizontal_lines_points(),
                                self.generate_vertical_lines_points()))

        max_length = max(a[1] for a in all_points)
        p = random.choice(filter(lambda x: x[1] == max_length, all_points))
        if self.enemy_field[self.calc_index(p[0])] != EMPTY:
            raise Exception

        return p

    def get_random_field(self):
        try:
            p = self.get_random_filtered_point()
            return self.calc_index(p[0])
        except:
            pass

        return random.choice([i for i, v in enumerate(self.enemy_field) if v == EMPTY])

    def do_shot(self):
        if self.next_shot_index is None:
            index = self.get_random_field()
        else:
            index = self.next_shot_index

        self.last_shot_position = self.calc_position(index)

        self.next_shot_index = None  # Reset for next iteration
        print(self.last_shot_position)
        return self.convert_from_position(self.last_shot_position)

    def after_enemy_ship_killed(self):
        """After enemy ship has killed, we need markup skip border around this one."""
        self.disable_for_shot_all_near()
        self.last_shot_damage = None

    def after_enemy_ship_damaged(self):
        self.last_shot_damage = self.last_shot_position
        self.try_detect_next_ship_cell()

    def after_our_miss(self):
        if self.last_shot_damage is not None:
            self.try_detect_next_ship_cell()

    def common_line_finder(self, pos, direction, c):
        print('cf pos {}, d {}, c {}'.format(pos, direction, c))

        def plus(p):
            new_p = list(p)
            new_p[c] += direction
            return tuple(new_p)

        checked_point = plus(pos)

        while True:
            if self.is_point_invalid(checked_point):
                return None

            if self.enemy_field[self.calc_index(checked_point)] == EMPTY:
                return checked_point

            if self.enemy_field[self.calc_index(checked_point)] in (SKIP, MISS):
                return None  # Nothing to do here

            checked_point = plus(checked_point)

    def vertical_finder(self, pos):
        return self.common_line_finder(pos, 1, 1) or self.common_line_finder(pos, -1, 1)

    def horizontal_finder(self, pos):
        return self.common_line_finder(pos, 1, 0) or self.common_line_finder(pos, -1, 0)

    def get_ship_layout_by_cell(self, cell):
        for p in self.nearest_generator(cell):
            if self.enemy_field[self.calc_index(p)] != SHIP:
                continue

            if p[0] == cell[0]:  # X the same, it's a vertical ship
                return LAYOUT_VERTICAL
            elif p[1] == cell[1]:  # Y the same, it's a horizontal ship
                return LAYOUT_HORIZONTAL

        return LAYOUT_UNKNOWN

    def try_detect_next_ship_cell(self):
        # If last cell is SHIP, be it is not dead - walk for sides to find other cells
        ship_layout = self.get_ship_layout_by_cell(self.last_shot_damage)
        finders = []
        if ship_layout == LAYOUT_VERTICAL:
            # Change only Y to find point. Walk up or down until empty
            finders = [self.vertical_finder]
        elif ship_layout == LAYOUT_HORIZONTAL:
            # Change only X to find point. Walk left or right until empty
            finders = [self.horizontal_finder]
        elif ship_layout == LAYOUT_UNKNOWN:
            # We has not know ship type yet, will try all directions
            finders = [self.vertical_finder, self.horizontal_finder]

        for finder in finders:
            p = finder(self.last_shot_damage)
            if p:
                self.next_shot_index = self.calc_index(p)
                return
