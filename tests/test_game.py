# coding: utf-8
from __future__ import unicode_literals
from seabattle.game import Game

import pytest


@pytest.fixture
def game():
    g = Game()
    g.start_new_game()

    return g


@pytest.fixture
def game_with_field(game):
    field = [0, 0, 0, 0, 0, 0, 1, 0, 0, 1,
             1, 1, 1, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 1, 0, 1, 0, 1, 0, 0,
             1, 1, 0, 1, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
             0, 1, 0, 1, 0, 1, 1, 1, 0, 0,
             0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    game.start_new_game(field=field)

    return game


@pytest.fixture
def enemy_field(game):
    field = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 1, 1, 0, 0, 0, 0, 1, 1, 1]

    game.enemy_field = field
    return field


def test_helper_functions(game):
    assert game.calc_index((4, 7)) == 63

    assert game.calc_position(63) == (4, 7)

    # assert game.convert_to_position('a10') == (1, 10)
    # assert game.convert_to_position('d 7') == (5, 7)
    # assert game.convert_to_position('д 5') == (5, 5)
    # assert game.convert_to_position('g 3') == (4, 3)

    # assert game.convert_to_position('k 1') == (10, 1)
    # assert game.convert_to_position('k 2') == (10, 2)
    # assert game.convert_to_position('k 10') == (10, 10)
    # assert game.convert_to_position('k два') == (10, 2)

    # assert game.convert_to_position('d пять') == (5, 5)

    assert game.convert_to_position('10 10') == (10, 10)
    assert game.convert_to_position('1 10') == (1, 10)
    assert game.convert_to_position('10 1') == (10, 1)
    assert game.convert_to_position('1 2') == (1, 2)
    assert game.convert_to_position('8 4') == (8, 4)
    assert game.convert_to_position('восемь четыре') == (8, 4)

    # assert game.convert_to_position('уже 4') == (7, 4)
    # assert game.convert_to_position('the 4') == (8, 4)
    # assert game.convert_to_position('за 4') == (8, 4)

    with pytest.raises(ValueError):
        assert game.convert_to_position('1') == (1, 1)

    # with pytest.raises(ValueError):
    #    game.convert_to_position('т шесть')

    # with pytest.raises(ValueError):
    #    game.convert_to_position('д пятнадцать')

    # assert game.convert_from_position((1, 1)) == 'а, 1'
    # assert game.convert_from_position((6, 5)) == 'е, 5'
    assert game.convert_from_position((6, 5), numbers=True) == '6, 5'


def test_shot(game_with_field):
    assert game_with_field.handle_enemy_shot((10, 1)) == 'hit'
    assert game_with_field.handle_enemy_shot((10, 2)) == 'kill'

    assert game_with_field.handle_enemy_shot((1, 10)) == 'kill'


def test_dead_ship(game_with_field):
    assert game_with_field.handle_enemy_shot((7, 1)) == 'kill'

    assert game_with_field.handle_enemy_shot((1, 5)) == 'hit'
    assert game_with_field.handle_enemy_shot((2, 5)) == 'kill'

    assert game_with_field.handle_enemy_shot((1, 2)) == 'hit'
    assert game_with_field.handle_enemy_shot((2, 2)) == 'hit'
    assert game_with_field.handle_enemy_shot((3, 2)) == 'kill'


def test_repeat(game):
    game.last_shot_position = (5, 7)
    assert '5, 7' == game.repeat()


def test_handle_shot(game_with_field):
    assert game_with_field.handle_enemy_shot((4, 7)) == 'hit'
    assert game_with_field.handle_enemy_shot((4, 7)) == 'hit'

    assert game_with_field.handle_enemy_shot((7, 1)) == 'kill'
    assert game_with_field.handle_enemy_shot((7, 1)) == 'kill'

    assert game_with_field.handle_enemy_shot((4, 2)) == 'miss'

    with pytest.raises(ValueError):
        game_with_field.handle_enemy_shot((19, 6))


def test_handle_reply(game):
    game.do_shot()
    game.handle_enemy_reply('miss')


def test_disable_for_shot_all_near(game, enemy_field):
    for last_shot in [
        (5, 5),
        (1, 1),
        (10, 1),
        (1, 10),
        (9, 10)
    ]:
        game.last_shot_position = last_shot
        game.disable_for_shot_all_near()
    assert game.enemy_field == [1, 5, 0, 0, 0, 0, 0, 0, 5, 1,
                                1, 5, 0, 0, 0, 0, 0, 0, 5, 1,
                                1, 5, 0, 0, 0, 0, 0, 0, 5, 1,
                                5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                                0, 0, 5, 1, 1, 1, 1, 5, 0, 0,
                                0, 0, 5, 5, 5, 5, 5, 5, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                5, 5, 5, 5, 0, 0, 5, 5, 5, 5,
                                1, 1, 1, 5, 0, 0, 5, 1, 1, 1]


@pytest.mark.parametrize('enemy_field, last_shot, next_shot', [
    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 1, 1, 1, 1, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (4, 5), (8, 5)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 1, 1, 1, 1, 5, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (4, 5), (3, 5)),

    ([0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (10, 1), (7, 1)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 1, 1, 1], (8, 10), (7, 10)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (2, 5), (2, 8)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (2, 5), (2, 4)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (2, 5), (2, 6)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (2, 5), (2, 4)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (2, 5), (3, 5)),

    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 1, 5, 0, 0, 0, 0, 0, 0, 0,
      0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0], (2, 5), (1, 5)),
])
def test_detect_next_shot(game, enemy_field, last_shot, next_shot):
    game.last_shot_damage = last_shot
    game.enemy_field = enemy_field
    game.try_detect_next_ship_cell()
    assert game.calc_position(game.next_shot_index) == next_shot
