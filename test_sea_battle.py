import unittest, time
from unittest.mock import Mock, patch, ANY
from pprint import pprint
import my_logger
from my_logger import log
import sea_battle
from sea_battle import SeaBattle
from sea_battle import WOUND
from sea_battle import KILL
from sea_battle import MISSED
from sea_battle import SHIP
from sea_battle import NOT_PERSPECTIVE
from sea_battle import EMPTY
from sea_battle import WIDTH
from sea_battle import DEEP
from sea_battle import UNKNOWN

class TestSeaBattle(unittest.TestCase):
    '''Тесты для морского боя'''
    def test_check_place(self):
        '''self, x: str, y: int, my_board: dict'''
        my_board =  {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'б': [' ', '⎕', '⎕', ' ', '⎕', '⎕', '⎕', ' ', '⎕', ' '],
                      'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'г': [' ', ' ', ' ', '⎕', '⎕', ' ', ' ', ' ', ' ', '⎕'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '⎕'],
                      'е': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '⎕'],
                      'ж': [' ', ' ', '⎕', '⎕', ' ', ' ', ' ', ' ', ' ', ' '],
                      'з': ['⎕', ' ', ' ', ' ', ' ', '⎕', '⎕', '⎕', '⎕', ' '],
                      'и': [' ', ' ', '⎕', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

        send_mock = Mock(return_value=True)
        bot = SeaBattle('url')
        bot.check_valid_place = send_mock
        self.assertFalse(bot.check_place(x='и',y=5,my_board=my_board))
        self.assertFalse(bot.check_place(x='з',y=4,my_board=my_board))
        self.assertFalse(bot.check_place(x='з', y=1, my_board=my_board))
        self.assertFalse(bot.check_place(x='ж', y=1, my_board=my_board))
        self.assertFalse(bot.check_place(x='и', y=1, my_board=my_board))
        self.assertFalse(bot.check_place(x='з', y=2, my_board=my_board))

    def test_check_hit(self):
        '''Проверка попадания'''
        my_board =   {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', SHIP],
                      'б': [' ', ' ', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' ', SHIP],
                      'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', SHIP],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', ' ', SHIP],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', SHIP, ' ', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' ']}

        status_living_ships =    {1: {'hits': 4, 'place': [('а', 10), ('б', 10), ('в', 10), ('г', 10)]},
                                  2: {'hits': 3, 'place': [('б', 3), ('б', 4), ('б', 5)]},
                                  3: {'hits': 3, 'place': [('е', 4), ('е', 5), ('е', 6)]},
                                  4: {'hits': 2, 'place': [('и', 6), ('и', 7)]},
                                  5: {'hits': 2, 'place': [('ж', 8), ('ж', 9)]},
                                  6: {'hits': 2, 'place': [('г', 6), ('г', 7)]},
                                  7: {'hits': 1, 'place': [('й', 4)]},
                                  8: {'hits': 1, 'place': [('е', 2)]},
                                  9: {'hits': 1, 'place': [('з', 4)]},
                                  10: {'hits': 1, 'place': [('з', 2)]}}


        send_mock = Mock(return_value=('а 1'))
        game = SeaBattle('url')
        game.bot_board = my_board  #подменяем поле
        game.status_bots_living_ships = status_living_ships
        game.bot_turn = send_mock
        game.stage = 'user must try to hit'
        game.remaining_bots_ships = [4,3,3,2,2,2,1,1,1,1]
        self.assertEqual(game.check_hit(turn='а 1'),('Мимо! Мой ход: а 1','wait answer from user'))
        self.assertEqual(game.check_hit(turn='а2'), ('Мимо! Мой ход: а 1', 'wait answer from user'))
        self.assertEqual(game.check_hit(turn='А 3'), ('Мимо! Мой ход: а 1', 'wait answer from user'))
        self.assertEqual(game.check_hit(turn='А4'), ('Мимо! Мой ход: а 1', 'wait answer from user'))
        self.assertEqual(game.check_hit(turn='а11'), ('Не понял', 'user must try to hit'))
        self.assertEqual(game.check_hit(turn='а 11'), ('Не понял', 'user must try to hit'))
        self.assertEqual(game.check_hit(turn='з4'), ('Убил!', 'user must try to hit'))
        self.assertEqual(game.check_hit(turn='г6'), ('Ранил!', 'user must try to hit'))
        self.assertEqual(game.check_hit(turn='е5'), ('Ранил!', 'user must try to hit'))
        game.bot_board['й'][0] = '⊡'  # ⊡ Раненый корабль
        self.assertEqual(game.check_hit(turn='й1'), ('Уже было, давай другое место!', 'user must try to hit'))
        game.bot_board['й'][0] = '⛝'  # ⛝ Убитый корабль
        self.assertEqual(game.check_hit(turn='й1'), ('Уже было, давай другое место!', 'user must try to hit'))
        game.bot_board['й'][0] = 'ͦ'  # ͦ Промах
        self.assertEqual(game.check_hit(turn='й1'), ('Уже было, давай другое место!', 'user must try to hit'))
        game.bot_board['й'][0] = '≋'  # '≋' выставляется автоматом вокруг найденных кораблей.
        self.assertEqual(game.check_hit(turn='й1'), ('Уже было, давай другое место!', 'user must try to hit'))

    def test_search_ortogonal_surround(self):
        '''Составление словаря ортогонального окружения точки'''
        my_board =   {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game = SeaBattle('url')
        # game.my_board = my_board  # подменять поле не требуется
        result = game.search_ortogonal_surround(x='а', y=1)
        checking_dict = {'d': ('а', 2), 'r': ('б', 1)}
        self.assertEqual(result,checking_dict)
        result = game.search_ortogonal_surround(x='й', y=10)
        checking_dict = {'l': ('и', 10), 'u': ('й', 9)}
        self.assertEqual(result,checking_dict)
        result = game.search_ortogonal_surround(x='г', y=1)
        checking_dict = {'d': ('г', 2), 'l': ('в', 1), 'r': ('д', 1)}
        self.assertEqual(result,checking_dict)
        result = game.search_ortogonal_surround(x='а', y=5)
        checking_dict = {'d': ('а', 6), 'r': ('б', 5), 'u': ('а', 4)}
        self.assertEqual(result,checking_dict)
        result = game.search_ortogonal_surround(x='й', y=5)
        checking_dict = {'d': ('й', 6), 'l': ('и', 5), 'u': ('й', 4)}
        self.assertEqual(result,checking_dict)
        result = game.search_ortogonal_surround(x='г', y=5)
        checking_dict = {'d': ('г', 6), 'l': ('в', 5), 'r': ('д', 5), 'u': ('г', 4)}
        self.assertEqual(result,checking_dict)

    def test_search_full_surround(self):
        '''Составление словаря ортогонального окружения точки'''
        my_board =   {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game = SeaBattle('url')
        # поле только для удобства и красоты
        result = game.search_full_surround(x='а', y=1)
        checking_dict = {'d': ('а', 2), 'r': ('б', 1), 'rd': ('б', 2)}
        self.assertEqual(result,checking_dict)
        result = game.search_full_surround(x='й', y=10)
        checking_dict = {'l': ('и', 10), 'lu': ('и', 9), 'u': ('й', 9)}
        self.assertEqual(result,checking_dict)
        result = game.search_full_surround(x='а', y=5)
        checking_dict = {'d': ('а', 6), 'r': ('б', 5), 'rd': ('б', 6), 'ru': ('б', 4), 'u': ('а', 4)}
        self.assertEqual(result,checking_dict)
        result = game.search_full_surround(x='в', y=10)
        checking_dict = {'l': ('б', 10), 'lu': ('б', 9), 'r': ('г', 10), 'ru': ('г', 9), 'u': ('в', 9)}
        self.assertEqual(result,checking_dict)
        result = game.search_full_surround(x='в', y=5)
        checking_dict = {'d': ('в', 6), 'l': ('б', 5), 'ld': ('б', 6), 'lu': ('б', 4), 'r': ('г', 5), 'rd': ('г', 6), 'ru': ('г', 4), 'u': ('в', 4)}
        self.assertEqual(result,checking_dict)

    def test_check_valid_place(self):
        '''Обрабатывает валидность точки в рамках поля. Если выходит, выдает False, при норме выдает True'''
        game = SeaBattle('url')
        self.assertTrue(game.check_valid_place(x='з', y=2))
        self.assertTrue(game.check_valid_place(x='а', y=1))
        self.assertTrue(game.check_valid_place(x='й', y=10))
        self.assertFalse(game.check_valid_place(x='к', y=10))
        self.assertFalse(game.check_valid_place(x='1', y=10))
        self.assertFalse(game.check_valid_place(x='а', y=11))
        self.assertFalse(game.check_valid_place(x='а', y=0))
        self.assertFalse(game.check_valid_place(x='а', y=-2))

    def test_check_phrase_about_try(self):
        '''Обрабатывает ответ игрока на валидность попытки. Если бот не понял, выдает False, если понял, то приводит к стандартному виду и отдает строкой'''
        game = SeaBattle('url')
        self.assertEqual(game.check_phrase_about_try(phrase='а1'),'а 1')
        self.assertEqual(game.check_phrase_about_try(phrase='а 1'),'а 1')
        self.assertEqual(game.check_phrase_about_try(phrase='А 1'),'а 1')
        self.assertEqual(game.check_phrase_about_try(phrase='А1'),'а 1')
        self.assertEqual(game.check_phrase_about_try(phrase='Й1'),'й 1')
        self.assertEqual(game.check_phrase_about_try(phrase='Й10'),'й 10')
        self.assertEqual(game.check_phrase_about_try(phrase='Й 10'),'й 10')
        self.assertEqual(game.check_phrase_about_try(phrase='Й,10'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='Й1.25'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='Й1,25'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='аа 1'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='аа1'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='а 0'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='а 11'), False)
        self.assertEqual(game.check_phrase_about_try(phrase='    '), False)

    def test_bot_turn(self):
        '''Игрок промахнулся, бот отвечает строкой вида "а 1"
        надо проверить реакцию на пустость или непустость self.assuming_hit
        наличие неналичия UNKNOWN в user_boards
        поиск единственного UNKNOWN в поле'''
        game = SeaBattle('url')
        user_board = {'а': ['*', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' ', 'О'],
                      'в': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': ['*', '*', '*', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': ['*', ' ', '*', '*', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': ['*', 'О', '*', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': ['*', ' ', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': ['*', 'О', '*', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': ['*', '*', '*', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', '*', '*', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        game.assuming_hit = []
        game.remaining_users_ships = [4,3,3,2,2,2,1,1,1,1]
        self.assertEqual(game.bot_turn(),ANY)
        self.assertEqual(game.previously_bot_turn, ANY)
        game.enemy_board['а'][0] = ' '
        game.enemy_board['в'][0] = ' '
        self.assertEqual(game.bot_turn(),'У меня кончились ходы, ты не жулик?')
        game.enemy_board['а'][0] = '*'
        game.enemy_board['а'][1] = '*'
        game.assuming_hit = [('а', 1)]
        self.assertEqual(game.bot_turn(), 'а 1')
        self.assertEqual(game.previously_bot_turn, ('а', 1))
        self.assertEqual(game.assuming_hit, [])
        self.assertEqual(game.previously_bot_turn, ('а', 1))

    def test_refactor(self):
        '''превращает строку вида 'а 1' в кортеж из ('a', 1)'''
        game = SeaBattle('url')
        self.assertEqual(game.refactor(phrase='а 1'), ('а', 1))
        self.assertEqual(game.refactor(phrase='й 1'), ('й', 1))
        self.assertEqual(game.refactor(phrase='а 10'), ('а', 10))
        self.assertEqual(game.refactor(phrase='в 7'), ('в', 7))
        self.assertEqual(game.refactor(phrase='н 12'), ('н', 12))

    def test_recourse_search(self):
        '''двигается рекурсивно в сторону матрицы движения, проверяя наличие WOUND'''
        game = SeaBattle('url')
        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', '*', WOUND, WOUND, '*', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(game.recourse_search(x='б', y=4, matrix_movement=(0, -1)), ('б', 2))
        self.assertEqual(game.recourse_search(x='б', y=4, matrix_movement=(0, 1)), ('б', 5))
        self.assertEqual(game.recourse_search(x='б', y=3, matrix_movement=(0, 1)), ('б', 5))
        self.assertEqual(game.recourse_search(x='б', y=5, matrix_movement=(0, -1)), ('б', 2))
        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', '*'],
                      'б': [' ', '*', WOUND, WOUND, '*', ' ', ' ', ' ', ' ', WOUND],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', WOUND],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', '*'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(game.recourse_search(x='б', y=10, matrix_movement=(1, 0)), ('г', 10))
        self.assertEqual(game.recourse_search(x='в', y=10, matrix_movement=(-1, 0)), ('а', 10))
        self.assertEqual(game.recourse_search(x='б', y=10, matrix_movement=(0, 1)), False)
        self.assertEqual(game.recourse_search(x='б', y=10, matrix_movement=(0, -1)), False)
        self.assertEqual(game.recourse_search(x='а', y=10, matrix_movement=(-1, 0)), False)
        self.assertEqual(game.recourse_search(x='й', y=10, matrix_movement=(1, 0)), False)
        self.assertEqual(game.recourse_search(x='й', y=10, matrix_movement=(0, 1)), False)
        self.assertEqual(game.recourse_search(x='б', y=10, matrix_movement=(0, 1)), False)
        self.assertEqual(game.recourse_search(x='б', y=10, matrix_movement=(0, -1)), False)
        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', '*'],
                      'б': [' ', '*', WOUND, WOUND, '*', ' ', ' ', ' ', ' ', WOUND],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', WOUND],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', '*'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', '*', '*', '*', '*', '*', '*', ' ', ' '],
                      'й': [' ', '*', WOUND, WOUND, WOUND, WOUND, WOUND, '*', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(game.recourse_search(x='й', y=3, matrix_movement=(0, 1)), ('й', 8))
        self.assertEqual(game.recourse_search(x='й', y=7, matrix_movement=(0, -1)), ('й', 2))


        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', '*'],
                      'б': [' ', '*', WOUND, WOUND, '*', ' ', ' ', ' ', ' ', WOUND],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', WOUND],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', '*'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', '*', '*', '*', '*', '*', '*', ' ', ' '],
                      'й': [' ', '*', WOUND, WOUND, WOUND, WOUND, WOUND, ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(game.recourse_search(x='й', y=3, matrix_movement=(0, 1)), False)
        self.assertEqual(game.recourse_search(x='й', y=5, matrix_movement=(0, -1)), ('й',2))

    def test_search_variants_for_hit_wounded_ships(self):
        '''Дополняет и возвращает список кортежей боту для более точного поиска и добивания корабля противника
        проверить на дополняемость передаваемого списка,
        '''
        # проверка на определение правильных концов корабля и сохранение потенциального списка целей
        game = SeaBattle('url')
        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', '*', WOUND, WOUND, '*', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(set(game.search_variants_for_hit_wounded_ships(x='б', y=3, assuming_hit=[])), set([('б', 5), ('б', 2)]))
        self.assertEqual(set(game.search_variants_for_hit_wounded_ships(x='б', y=4, assuming_hit=[])), set([('б', 5), ('б', 2)]))
        self.assertEqual(game.search_variants_for_hit_wounded_ships(x='ж', y=5, assuming_hit=[]), [])
        self.assertEqual(set(game.search_variants_for_hit_wounded_ships(x='б', y=4, assuming_hit=[('й', 1)])), set([('б', 5), ('б', 2),('й', 1)]))

        # проверка на определение правильного конца корабля, расположенного на краю поля
        user_board = {'а': [' ', ' ', WOUND, ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', '*', WOUND, '*', '*', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(game.search_variants_for_hit_wounded_ships(x='б', y=3, assuming_hit=[]), [('в', 3)])
        self.assertEqual(game.search_variants_for_hit_wounded_ships(x='а', y=3, assuming_hit=[]), [('в', 3)])

        # проверка на определение всех 4 потенциальных направлений при попадании в корабль
        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', '*', WOUND, '*', '*', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(set(game.search_variants_for_hit_wounded_ships(x='б', y=3, assuming_hit=[])), set([('в', 3), ('б', 2), ('б', 4), ('а', 3)]))

        # проверка на определение потенциальных направлений при попадании в корабль, если их не 4
        user_board = {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', '*', WOUND, '*', '*', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(set(game.search_variants_for_hit_wounded_ships(x='б', y=3, assuming_hit=[])), set([('в', 3), ('б', 2), ('б', 4)]))

        # проверка на удаление бесперспективных ортогональных направлений при определении ориентации корабля
        user_board = {'а': [' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', '*', WOUND, '*', '*', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', WOUND, ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', '*', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        game.enemy_board = user_board
        self.assertEqual(set(game.search_variants_for_hit_wounded_ships(x='в', y=3, assuming_hit=[('б', 2), ('б', 4), ('а', 3)])), set([('а', 3), ('г', 3)]))

    def test_check_killing_ship(self):
        '''Проверка ранил игрок или убил корабль бота'''
        # проверка на определение правильных концов корабля и сохранение потенциального списка целей
        game = SeaBattle('url')
        my_board =   {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' ', 'О'],
                      'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                      'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        status_living_ships =    {1: {'hits': 4, 'place': [('а', 10), ('б', 10), ('в', 10), ('г', 10)]},
                                  2: {'hits': 3, 'place': [('б', 3), ('б', 4), ('б', 5)]},
                                  3: {'hits': 3, 'place': [('е', 4), ('е', 5), ('е', 6)]},
                                  4: {'hits': 2, 'place': [('и', 6), ('и', 7)]},
                                  5: {'hits': 2, 'place': [('ж', 8), ('ж', 9)]},
                                  6: {'hits': 2, 'place': [('г', 6), ('г', 7)]},
                                  7: {'hits': 1, 'place': [('й', 4)]},
                                  8: {'hits': 1, 'place': [('е', 2)]},
                                  9: {'hits': 1, 'place': [('з', 4)]},
                                  10: {'hits': 1, 'place': [('з', 2)]}}
        game.bot_board = my_board
        game.status_bots_living_ships = status_living_ships
        # проверка убийства 1 палубного корабля, проверка удаления его из списка и отметка в поле
        game.stage = 'user must try to hit'
        game.remaining_bots_ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.assertEqual(game.check_killing_ship(place='з 2', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), ('Убил!', 'user must try to hit'))
        self.assertFalse(10 in game.status_bots_living_ships)
        self.assertEqual(game.bot_board['з'][1], KILL)

        my_board = {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                    'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' ', 'О'],
                    'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                    'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                    'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                    'е': [' ', 'О', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                    'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                    'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                    'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                    'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}
        status_living_ships = {1: {'hits': 4, 'place': [('а', 10), ('б', 10), ('в', 10), ('г', 10)]},
                               2: {'hits': 3, 'place': [('б', 3), ('б', 4), ('б', 5)]},
                               3: {'hits': 3, 'place': [('е', 4), ('е', 5), ('е', 6)]},
                               4: {'hits': 2, 'place': [('и', 6), ('и', 7)]},
                               5: {'hits': 2, 'place': [('ж', 8), ('ж', 9)]},
                               6: {'hits': 2, 'place': [('г', 6), ('г', 7)]},
                               7: {'hits': 1, 'place': [('й', 4)]},
                               8: {'hits': 1, 'place': [('е', 2)]},
                               9: {'hits': 1, 'place': [('з', 4)]},
                               10: {'hits': 1, 'place': [('з', 2)]}}
        game.bot_board = my_board
        game.status_bots_living_ships = status_living_ships
        # проверка ранения 2 палубного корабля, проверка его хитов в списке и отметки в поле
        self.assertEqual(game.check_killing_ship(place='и 6', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), ('Ранил!', 'user must try to hit'))
        self.assertEqual(game.status_bots_living_ships[4]['hits'], 1)
        self.assertEqual(game.bot_board['и'][5], WOUND)
        # проверка убийства этого 2 палубного корабля, проверка в списке и всех 2 отметок в поле
        self.assertEqual(game.check_killing_ship(place='и 7', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), ('Убил!', 'user must try to hit'))
        self.assertFalse(4 in game.status_bots_living_ships)
        self.assertEqual(game.bot_board['и'][5], KILL)
        self.assertEqual(game.bot_board['и'][6], KILL)
        # проверка ранения 3 палубного корабля, проверка в списке и отметок в поле
        self.assertEqual(game.check_killing_ship(place='е 4', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), ('Ранил!', 'user must try to hit'))
        self.assertEqual(game.status_bots_living_ships[3]['hits'], 2)
        self.assertEqual(game.bot_board['е'][3], WOUND)
        # проверка 2 ранения 3 палубного корабля, проверка в списке и отметок в поле
        self.assertEqual(game.check_killing_ship(place='е 5', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), ('Ранил!', 'user must try to hit'))
        self.assertEqual(game.status_bots_living_ships[3]['hits'], 1)
        self.assertEqual(game.bot_board['е'][4], WOUND)
        # проверка убийства 3 палубного корабля, проверка наличия в списке и отметок в поле
        self.assertEqual(game.check_killing_ship(place='е 6', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), ('Убил!', 'user must try to hit'))
        self.assertFalse(3 in game.status_bots_living_ships)
        self.assertEqual(game.bot_board['е'][3], KILL)
        self.assertEqual(game.bot_board['е'][4], KILL)
        self.assertEqual(game.bot_board['е'][5], KILL)

        # проверка конца игры
        status_living_ships = {9: {'hits': 1, 'place': [('з', 4)]}}
        game.status_bots_living_ships = status_living_ships
        game.remaining_bots_ships = [1]
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', ' '],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', ' ', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', '*', '*', ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', ' ', '*'],
                      'е': ['*', '*', '*', '*', '*', '*', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'з': [' ', '*', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', '*', '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', '*', ' ', ' ', ' ', ' ', '*', ' ']}
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nТы потопил все мои корабли!\nУ меня кораблей то и не осталось.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.check_killing_ship(place='з 4', board=game.bot_board, status=game.status_bots_living_ships, ships=game.remaining_bots_ships), (test_str, 'end the game'))
        self.assertFalse(9 in game.status_bots_living_ships)
        self.assertEqual(game.bot_board['з'][3], KILL)

    def test_filling_not_perspective(self):
        '''Заполняет поля убитого корабля KILL, вокруг него выставляет NOT_PERSPECTIVE по словарю {hits=2, place=[('a',1),('b',2)]}'''
        game = SeaBattle('url')
        user_board =   {'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '*', 'О'],
                      'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', '*', 'О'],
                      'в': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '*', 'О'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', 'О'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', 'О', '*', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', '*', ' ']}

        game.enemy_board = user_board
        # 4-палубник на краю
        testov_dict = {'hits': 4, 'place': [('а', 10), ('б', 10), ('в', 10), ('г', 10)]}
        game.filling_not_perspective(status_users_ship=testov_dict, board=user_board)
        for x,y in testov_dict['place']:
            self.assertEqual(game.enemy_board[x][y - 1], KILL)
        for x,y in [('а', 9), ('б', 9), ('в', 9), ('г', 9), ('д', 10),('д', 9),]:
            self.assertEqual(game.enemy_board[x][y - 1], NOT_PERSPECTIVE)
        # 1-палубный в центре
        testov_dict = {'hits': 1, 'place': [('е', 2)]}
        game.filling_not_perspective(status_users_ship=testov_dict, board=user_board)
        for x,y in testov_dict['place']:
            self.assertEqual(game.enemy_board[x][y - 1], KILL)
        for x,y in [('д', 1),('д', 2),('д', 3),('ж', 1),('ж', 2),('ж', 3),('е', 1),('е', 3)]:
            self.assertEqual(game.enemy_board[x][y - 1], NOT_PERSPECTIVE)
        # 1-палубный в углу
        testov_dict = {'hits': 1, 'place': [('й', 10)]}
        game.filling_not_perspective(status_users_ship=testov_dict, board=user_board)
        for x, y in testov_dict['place']:
            self.assertEqual(game.enemy_board[x][y - 1], KILL)
        for x, y in [('й', 9), ('и', 10), ('и', 9)]:
            self.assertEqual(game.enemy_board[x][y - 1], NOT_PERSPECTIVE)
        # pprint(game.user_board)

    def test_got_reply_about_our_turn(self):
        '''Обрабатывает ответ игрока на наш зависимости от результата. Также выдает ответ строкой. Если мы попали, сразу дает следующий ход в той же строке'''

        game = SeaBattle('url')
        user_board =   {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', 'О'],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', 'О', '*', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', '*', ' ']}
        game.enemy_board = user_board

        # проверка на ранил в углу 4-палубника

        game.previously_bot_turn = ('а', 10)
        send_mock = Mock(return_value='')
        game.bot_turn = send_mock  # чтобы не терять один вариант из перспективного хода
        game.stage = 'user must try to hit'
        game.remaining_users_ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.assertEqual(game.got_reply_about_our_turn(reply='ранил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['а'][9], WOUND)
        self.assertEqual(game.status_users_ship['hits'], 1)
        self.assertEqual(game.status_users_ship['place'], [('а', 10)])
        self.assertEqual(set(game.assuming_hit), set([('а', 9),('б', 10)]))
        game.previously_bot_turn = ('б', 10)
        game.assuming_hit.remove(('б', 10))
        self.assertEqual(game.got_reply_about_our_turn(reply='ранил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['б'][9], WOUND)
        self.assertEqual(game.status_users_ship['hits'], 2)
        self.assertEqual(game.status_users_ship['place'], [('а', 10),('б', 10)])
        self.assertEqual(game.assuming_hit, [('в', 10)])
        game.previously_bot_turn = ('в', 10)
        game.assuming_hit.remove(('в', 10))
        self.assertEqual(game.got_reply_about_our_turn(reply='ранил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['в'][9], WOUND)
        self.assertEqual(game.status_users_ship['hits'], 3)
        self.assertEqual(game.status_users_ship['place'], [('а', 10),('б', 10),('в', 10)])
        self.assertEqual(game.assuming_hit, [('г', 10)])
        game.previously_bot_turn = ('г', 10)
        game.assuming_hit.remove(('г', 10))
        self.assertEqual(game.got_reply_about_our_turn(reply='убил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['а'][9], KILL)
        self.assertEqual(game.enemy_board['б'][9], KILL)
        self.assertEqual(game.enemy_board['в'][9], KILL)
        self.assertEqual(game.enemy_board['г'][9], KILL)
        self.assertEqual(game.status_users_ship['hits'], 0)
        self.assertEqual(game.status_users_ship['place'], [])
        self.assertEqual(game.assuming_hit, [])
        self.assertEqual(game.remaining_users_ships, [3, 3, 2, 2, 2, 1, 1, 1, 1])

        # ранение в окруженной всеми * клетки
        game.previously_bot_turn = ('е', 2)
        self.assertEqual(game.got_reply_about_our_turn(reply='ранил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['е'][1], WOUND)
        self.assertEqual(game.status_users_ship['hits'], 1)
        self.assertEqual(game.status_users_ship['place'], [('е', 2)])
        self.assertEqual(set(game.assuming_hit), set([('д', 2),('е', 1),('е', 3),('ж', 2)]))
        game.status_users_ship['hits'] = 0  # обнуляем, чтобы не мешало следующему тесту

        # убийство 1 палубника
        game.previously_bot_turn = ('е', 2)
        game.assuming_hit = []
        self.assertEqual(game.got_reply_about_our_turn(reply='убил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['е'][1], KILL)
        self.assertEqual(game.status_users_ship['hits'], 0)
        self.assertEqual(game.status_users_ship['place'], [])
        self.assertEqual(game.assuming_hit, [])
        self.assertEqual(game.remaining_users_ships, [3, 3, 2, 2, 2, 1, 1, 1])

        # ранение в середину 3-палубника
        game.previously_bot_turn = ('б', 4)
        self.assertEqual(game.got_reply_about_our_turn(reply='ранил'),(ANY,'wait answer from user'))
        self.assertEqual(game.enemy_board['б'][3], WOUND)
        self.assertEqual(game.status_users_ship['hits'], 1)
        self.assertEqual(game.status_users_ship['place'], [('б', 4)])
        self.assertEqual(set(game.assuming_hit), set([('в', 4), ('б', 3), ('б', 5), ('а', 4)]))
        game.previously_bot_turn = ('б', 3)
        game.assuming_hit.remove(('б', 3))
        self.assertEqual(game.got_reply_about_our_turn(reply='ранил'), (ANY, 'wait answer from user'))
        self.assertEqual(game.enemy_board['б'][2], WOUND)
        self.assertEqual(game.status_users_ship['hits'], 2)
        self.assertEqual(game.status_users_ship['place'], [('б', 4),('б', 3)])
        self.assertEqual(set(game.assuming_hit), set([('б', 2), ('б', 5)]))
        game.previously_bot_turn = ('б', 2)
        game.assuming_hit.remove(('б', 2))
        self.assertEqual(game.got_reply_about_our_turn(reply='мимо'), (ANY, 'user must try to hit'))
        self.assertEqual(game.enemy_board['б'][1], MISSED)
        self.assertEqual(game.status_users_ship['hits'], 2)
        self.assertEqual(game.status_users_ship['place'], [('б', 4),('б', 3)])
        self.assertEqual(set(game.assuming_hit), set([('б', 5)]))
        game.previously_bot_turn = ('б', 5)
        game.assuming_hit.remove(('б', 5))
        self.assertEqual(game.got_reply_about_our_turn(reply='убил'), (ANY, 'wait answer from user'))
        self.assertEqual(game.enemy_board['б'][4], KILL)
        self.assertEqual(game.status_users_ship['hits'], 0)
        self.assertEqual(game.status_users_ship['place'], [])
        self.assertEqual(game.assuming_hit, [])
        self.assertEqual(game.remaining_users_ships, [3, 2, 2, 2, 1, 1, 1])

        # проверка на конец игры
        game.remaining_users_ships = [1]
        game.previously_bot_turn = ('й', 4)
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', 'О'],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', 'О', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', 'О', '*'],
                      'е': ['*', 'О', '*', 'О', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', 'О', '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', '*', ' ']}
        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1,1,1]
        game.bot_board = my_board
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nЯ потопил все твои корабли!\nУ меня осталось: 1 фрегат, 3 корвета, 6 катеров.\nУ тебя кораблей то и не осталось.'
        self.assertEqual(game.got_reply_about_our_turn(reply='убил'), (test_str, 'end the game'))
        self.assertEqual(game.enemy_board['й'][3], KILL)
        self.assertEqual(game.status_users_ship['hits'], 0)
        self.assertEqual(game.status_users_ship['place'], [])
        self.assertEqual(game.assuming_hit, [])

        # Проверка на мимо
        game.remaining_users_ships = [4, 3, 2, 1]
        game.previously_bot_turn = ('г', 1)
        self.assertEqual(game.got_reply_about_our_turn(reply='мимо'), (ANY, 'user must try to hit'))
        self.assertEqual(game.enemy_board['г'][0], MISSED)

        # Проверка на пошел на хер
        game.remaining_users_ships = [4, 3, 2, 1]
        game.previously_bot_turn = ('г', 1)
        self.assertEqual(game.got_reply_about_our_turn(reply='пошел нахер'), ('Эээ, не понял. Повтори!', 'wait answer from user'))
        self.assertEqual(game.enemy_board['г'][0], MISSED)

    def test_count_result_game(self):
        '''Вычисляет по окончании игры оставшиеся корабли и выдает строку и число выживших судов'''
        board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game = SeaBattle('url')
        ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        test_str = 'осталось: 1 фрегат, 3 корвета, 5 катеров'
        self.assertEqual(game.count_result_game(board=board,ships=ships),(test_str,14))
        ships = [3, 2, 2, 2, 1, 1, 1, 1, 1,1,1]
        test_str = 'осталось: 1 фрегат, 3 корвета, 7 катеров'
        self.assertEqual(game.count_result_game(board=board,ships=ships),(test_str,14))
        ships = [x for x in range(1,33)]
        test_str = 'осталось: 1 катер, 1 корвет, 1 фрегат, 1 крейсер, 1 линкор, 1 суперлинкор, 1 мегалинкор, 1 гигалинкор, 1 суперпуперлинкор, 1 годзилолинкор, 1 эльфбот, 1 цвольбот, 1 драйцейнбот, 1 фюрцейнбот, 1 фюнфцейнбот, 1 зексцейнбот, 1 зибенцейнбот, 1 ахтцейнбот, 1 найнцейнбот, 1 цванцигбот, 1 цванцигайнцбот, 1 цванциццвайбот, 1 цванцицдрайбот, 1 цванцицфюрбот, 1 цванцицфюнфбот, 1 цванцицсексбот, 1 цванцицзибенбот, 1 цванцицахтбот, 1 цванцицнайнбот, 1 драйцихбот, 1 драйцихайнцбот, 1 надо_же_какой_ты_упорный_бот'
        self.assertEqual(game.count_result_game(board=board, ships=ships), (test_str, 14))
        ships = []
        test_str = 'кораблей то и не осталось'
        self.assertEqual(game.count_result_game(board=board, ships=ships), (test_str, 14))
        # проверяем подсчёт, когда нет пользовательского поля
        board = {}
        ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.status_users_ship['hits'] = 0
        test_str = 'осталось: 1 фрегат, 3 корвета, 5 катеров'
        self.assertEqual(game.count_result_game(board=board,ships=ships),(test_str,14))
        board = {}
        ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.status_users_ship['hits'] = 1
        test_str = 'осталось: 1 фрегат, 3 корвета, 5 катеров'
        self.assertEqual(game.count_result_game(board=board,ships=ships),(test_str,13))

    def test_result_game(self):
        '''Вычисляет ответ юзеру при любом окончании игры'''
        game = SeaBattle('url')
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nПо очкам ничья. 14 и 14\nУ меня осталось: 1 фрегат, 3 корвета, 5 катеров.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1]
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nТвоя победа по очкам: 14 против 13\nУ меня осталось: 1 фрегат, 3 корвета, 4 катера.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', SHIP, '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', SHIP, '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1,1,1]
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nМоя победа по очкам: 15 против 14\nУ меня осталось: 1 фрегат, 3 корвета, 6 катеров.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', ' '],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', ' ', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', '*', '*', ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', ' ', '*'],
                      'е': ['*', '*', '*', '*', '*', '*', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      'з': [' ', '*', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', '*', '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', '*', ' ', ' ', ' ', ' ', '*', ' ']}
        game.remaining_bots_ships = []
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nТы потопил все мои корабли!\nУ меня кораблей то и не осталось.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', SHIP, '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', SHIP, '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1,1,1]
        game.bot_board = my_board
        game.remaining_users_ships = []
        game.lazy_user_board = {}
        test_str = 'Вот и кончилась наша игра.\nЯ потопил все твои корабли!\nУ меня осталось: 1 фрегат, 3 корвета, 6 катеров.\nУ тебя кораблей то и не осталось.'
        self.assertEqual(game.result_game(),(test_str))

        # когда бот ведет поле игрока и у них одинаковое количество оставшихся в живых кораблей
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = my_board
        test_str = 'Вот и кончилась наша игра.\nПо очкам ничья. 14 и 14\nУ меня осталось: 1 фрегат, 3 корвета, 5 катеров.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

        #список кораблей одинаковый, но на поле у игрока один корабль ранен
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        user_board = {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                    'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                    'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                    'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                    'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                    'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                    'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                    'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                    'и': [' ', ' ', ' ', ' ', ' ', SHIP, '*', ' ', '*', '*'],
                    'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.lazy_user_board = user_board
        test_str = 'Вот и кончилась наша игра.\nМоя победа по очкам: 14 против 13\nУ меня осталось: 1 фрегат, 3 корвета, 5 катеров.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

        # когда бот не ведет поле игрока, но у игрока ранен один корабль
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', SHIP],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', ' ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', SHIP, '*', SHIP, SHIP, SHIP, ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', SHIP, SHIP, ' '],
                      'з': [' ', SHIP, ' ', SHIP, ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', SHIP, SHIP, ' ', '*', '*'],
                      'й': [' ', ' ', ' ', SHIP, ' ', ' ', ' ', ' ', '*', ' ']}

        game.remaining_bots_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.bot_board = my_board
        game.remaining_users_ships = [3, 2, 2, 2, 1, 1, 1, 1, 1]
        game.lazy_user_board = {}
        game.status_users_ship['hits'] = 1
        test_str = 'Вот и кончилась наша игра.\nМоя победа по очкам: 14 против 13\nУ меня осталось: 1 фрегат, 3 корвета, 5 катеров.\nУ тебя осталось: 1 фрегат, 3 корвета, 5 катеров.'
        self.assertEqual(game.result_game(),(test_str))

    def test_show_users_boards(self):
        '''Показывает 1 или оба поля пользователя. Слева lazy_users_board или пустой, а второй генерится на основе my_board бота '''
        game = SeaBattle('url')
        enemy_board ={'а': [' ', '*', '*', '*', '*', ' ', '≋', '≋', '≋', '*'],
                      'б': ['*', '*', '*', '*', '*', '*', '≋', '®', '≋', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', '≋', '≋', '≋', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', '*', '*', ' ', '*', '*'],
                      'д': ['*', '*', '*', 'ͦ', '≋', '≋', ' ', ' ', '*', '*'],
                      'е': ['*', '*', '*', 'ø', 'ø', 'ø', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', '≋', 'ͦ', '≋', ' ', '*', '*', ' '],
                      'з': [' ', '*', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', ' ', ' ', ' ', '*', '*', ' ', '*', '*'],
                      'й': [' ', ' ', ' ', '*', ' ', ' ', ' ', ' ', '*', ' ']}
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', 'О'],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', 'ͦ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', 'О', '*', 'ø', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', '≋', '≋', '≋', 'О', 'О', ' ', '*', '*'],
                      'й': [' ', ' ', '≋', '®', '≋', ' ', ' ', ' ', '*', ' ']}

        game.lazy_user_board = {}
        game.bot_board = my_board
        game.enemy_board = enemy_board
        dict1 = ANY
        dict2 = ANY
        self.assertEqual(game.show_users_boards(), (dict1,dict2))

        lazy_user_board ={'а': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О'],
                          'б': [' ', ' ', 'О', 'О', 'О', ' ', ' ', ' ', ' ', 'О'],
                          'в': [' ', ' ', ' ', 'ͦ', ' ', ' ', ' ', ' ', ' ', 'О'],
                          'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', 'О'],
                          'д': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                          'е': [' ', '®', ' ', 'ø', 'О', 'О', ' ', ' ', ' ', ' '],
                          'ж': [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                          'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                          'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', ' ', ' '],
                          'й': [' ', ' ', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' ']}

        game.lazy_user_board = lazy_user_board
        self.assertEqual(game.show_users_boards(), (dict1, dict2))

    def test_replace_obj_in_boards(self):
        '''Меняет во входящем словаре old на new'''
        game = SeaBattle('url')
        my_board =      {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', 'О'],
                      'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                      'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                      'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                      'д': ['*', '*', '*', ' ', 'ͦ', ' ', ' ', ' ', '*', '*'],
                      'е': ['*', 'О', '*', 'ø', 'О', 'О', ' ', ' ', ' ', ' '],
                      'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                      'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                      'и': [' ', ' ', '≋', '≋', '≋', 'О', 'О', ' ', '*', '*'],
                      'й': [' ', ' ', '≋', '®', '≋', ' ', ' ', ' ', '*', ' ']}
        dict1 =    {'а': [' ', '*', '*', '*', '*', ' ', ' ', ' ', '*', 'О'],
                    'б': ['*', '*', '*', '*', '*', '*', '*', ' ', '*', '*'],
                    'в': [' ', '*', '*', '*', '*', '*', ' ', ' ', '*', '*'],
                    'г': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                    'д': ['*', '*', '*', ' ', 'ͦ', ' ', ' ', ' ', '*', '*'],
                    'е': ['*', 'О', '*', 'ø', 'О', 'О', ' ', ' ', ' ', ' '],
                    'ж': ['*', '*', '*', ' ', ' ', ' ', ' ', 'О', 'О', ' '],
                    'з': [' ', 'О', ' ', 'О', ' ', ' ', ' ', ' ', ' ', ' '],
                    'и': [' ', ' ', ' ', ' ', ' ', 'О', 'О', ' ', '*', '*'],
                    'й': [' ', ' ', ' ', '®', ' ', ' ', ' ', ' ', '*', ' ']}

        self.assertEqual(game.replace_obj_in_boards(dirty_board=my_board,old=NOT_PERSPECTIVE,new=EMPTY), (dict1))


if __name__ == '__main__':
    unittest.main()