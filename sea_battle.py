'''Можно добавить при поиске случайной цели составление списка более перспективных мест, когда в списке целей имеются
корабли больше 1 палубы: сканировать поле на составление списков точек с максимальным ортогональным количеством unknown
вставить это на сложности 2 и 3
todo Еще в чате приходится что-то посылать боту, чтобы тот посмотрел результат в своей доске, это надо исправить
'''

import os
import time, random, re
from pprint import pprint
import logging
from rich import print, box
from rich.console import Console
from rich.table import Table

log = logging.getLogger('sea_battle')
fh = logging.FileHandler("log/seabattle.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)
log.setLevel(logging.INFO)

WIDTH = 'й'  # Ширина поля
DEEP = 10    # по умолчанию поле 10х10

WOUND = '⊡' # '\u22A1' ⊡ Раненый корабль
KILL = '⛝'  # chr(9949) ⛝ Убитый корабль
MISSED = chr(1607)  # Промах
SHIP = '⎈'  # chr(9096) Целый корабль
NOT_PERSPECTIVE = '\u224B'  # '≋' выставляется автоматом вокруг найденных кораблей.
EMPTY = ' '  #
UNKNOWN = '*'  # еще не проверенная для удара клетка
COLOR_SCHEME = {}  # словарь окраски символов
COLOR_SCHEME[WOUND] = '[red]'
COLOR_SCHEME[KILL] = '[red]'
COLOR_SCHEME[MISSED] = '[blue]'
COLOR_SCHEME[SHIP] = '[green]'
COLOR_SCHEME[EMPTY] = '[black]'
COLOR_SCHEME[UNKNOWN] = '[green]'

class SeaBattle:
    names_ships = {1: 'катер', 2: 'корвет', 3: 'фрегат', 4: 'крейсер', 5: 'линкор', 6: 'суперлинкор', 7: 'мегалинкор',
                   8: 'гигалинкор', 9: 'суперпуперлинкор', 10: 'годзилолинкор', 11: 'эльфбот', 12: 'цвольбот',
                   13: 'драйцейнбот', 14: 'фюрцейнбот', 15: 'фюнфцейнбот', 16: 'зексцейнбот', 17: 'зибенцейнбот',
                   18: 'ахтцейнбот', 19: 'найнцейнбот', 20: 'цванцигбот', 21: 'цванцигайнцбот', 22: 'цванциццвайбот',
                   23: 'цванцицдрайбот', 24: 'цванцицфюрбот', 25: 'цванцицфюнфбот', 26: 'цванцицсексбот',
                   27: 'цванцицзибенбот',
                   28: 'цванцицахтбот', 29: 'цванцицнайнбот', 30: 'драйцихбот', 31: 'драйцихайнцбот',
                   32: 'надо_же_какой_ты_упорный_бот'}

    def __init__(self, user):
        self.id = user.id
        self.user = user  # сохраняем экземпляр пользователя
        self.assuming_hit = []  #список более вероятных целей бота, формируется при попадании в корабль игрока
        self.previously_bot_turn = ('а',1)  # кортеж для хранения хода бота, чтобы занести результат после ответа игрока
        self.status_bots_living_ships = {}  # словарь для хранения статусов кораблей бота dict(1: dict(hits=4, place=[('a',1),('a',2),('a',3),('a',4)]))
        self.status_users_living_ships = {}  # словарь для хранения статусов кораблей юзера
        self.status_users_ship = {'hits':0, 'place': []}  #  словарь для текущей жертвы бота, чтобы потом заменить раненых на убитых, а вокруг корабля поставить знаки неперспективно
        self.lazy_user_board = {}  # по умолчанию пустой словарь, но для ленивых игроков, бот может сам расставлять их корабли и показывать его
        self.enemy_board = {}  #предполагаемое для бота поле игрока
        self.stage = self.start_game
        self.show_every_turn = False  # переменная показывания поля каждый ход
        self.bot_board = {}
        self.cheat_list = []

    def cheat_bot_board(self) -> list:
        '''Убирает с поля бота 1-палубный корабль, если таковой есть, оставляя его в списке кораблей, а затем составляет
        список потенциальных мест для него и рисует его только тогда, когда такое место остается лишь 1'''
        search = None
        for key in self.status_bots_living_ships.keys():  # ищем самый последний из 1-палубников
            if self.status_bots_living_ships[key]['hits'] == 1:
                search = key
        if not search:  # если 1-палубников нет, возвращаем пустой список, то есть бот читить не будет
            return []
        x, y = self.status_bots_living_ships[search]['place'][0]
        self.status_bots_living_ships[search]['place'] = [('0', 0)]
        self.cheat_number = search
        self.bot_board[x][y-1] = EMPTY
        cheat_list = []
        for key in self.bot_board.keys():
            for place in range(DEEP):
                if self.bot_board[key][place] == EMPTY:
                    surround = self.search_full_surround(x=key,y=place+1)
                    for x_ord, y_ord in surround.values(): # если в окружении нет корабля, то это потенциальное место для нашего корабля-призрака.
                        if self.bot_board[x_ord][y_ord-1] == SHIP:
                            break
                    else:
                        cheat_list.append((key,place+1))
        return cheat_list

    def create_board(self):
        '''создает поле бота или ленивого игрока, случайным перебором возможных мест с проверкой валидности'''
        my_board = {}
        actual_ships = {}
        for number in range(1072, ord(WIDTH) + 1):
            my_board[chr(number)] = [' ' for _ in range(DEEP)]   # {'a':[' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],...
        time_start_create = time.time()  # для контроля ухода в бесконечный цикл при слишком большом кол-ве кораблей
        number_ship = 1
        ships = self.ships[:]
        while ships:  # пока список непустой
            current_time = time.time()
            if (current_time - time_start_create) > 2:  # поле создается более 2 секунд, какой-то косяк
                raise TimeoutError
            x = random.choice([chr(x) for x in range(1072, ord(WIDTH)+1)])
            y = random.randint(1, DEEP)
            ship = ships[0]                                     # берем самый левый из оставшихся
            place = self.check_placing(x, y, ship, my_board)    # возвращает либо False, то есть нельзя сюда,
                                                                # либо cписок кортежей куда пихается [('a',1),('б','1')]
            if not place:   # значит сюда нельзя запихнуть
                continue    # пробуем новый рандом
            for part in range(ship):    # раз сюда дошло, значит прошло проверку валидности расположения
                x, y = place[part]      # извлекаем валидные места
                my_board[x][y - 1] = SHIP
            deleted_ship = ships.pop(0)     # удаляем корабль из списка и продолжаем пока список не опустеет
            actual_ships[number_ship] = dict(hits=deleted_ship, place=place)  # словарь всех кораблей
            number_ship += 1
        return (my_board, actual_ships)

    def check_placing(self, x: str, y: int, ship: int, my_board: dict):
        '''Проверяет можно ли расположить корабль хоть как-то в указанном месте, если нет возвращает False
	   если можно, то возвращает список кортежей мест [('a',1), ('б', 1)]'''
        place = []
        down = right = False
        while ship:  # работает пока длина корабля не равна 0
            variant = self.check_place(x, y, my_board)
            if not variant:  # то есть нельзя сюда поставить, выходим
                return False
            place.append(variant)  # сохраняем точку и прикидываем куда дальше ставить корабль
            if not down and not right:  # мы еще не выбрали в какую сторону развиваться
                if y + ship >= DEEP + 2:  # если он не влазит вниз
                    if ord(x) + ship >= ord(WIDTH) + 2:  # ord('к') = 1082 # и не влазит вправо
                        return False
                    else:
                        right = True
                else:
                    down = True
            if right and down:  # если в оба места можно, то рандомный выбор
                choice = random.randint(1, 2)
                if choice == 1:
                    down = False
                else:
                    right = False
            if down:
                y += 1
            else:
                x = chr(ord(x) + 1)
            ship -= 1  # уменьшаем длину корабля, пока тот не кончится
        return place  # список кортежей мест [('a',1), ('б', 1)]

    def check_place(self, x: str, y: int, my_board: dict):
        '''Проверяет можно ли расположить корабль или часть корабля в указанном месте, если нет возвращает False
	   если можно, то возвращает кортеж места'''
        if my_board[x][y - 1] != EMPTY:  # то есть место не пустое, сразу нафиг
            return False
        left = chr(ord(x) - 1); right = chr(ord(x) + 1); up = y-1; down = y + 1
        iter_dict = dict(l=(left, y), lu=(left, up), u=(x, up), ru=(right, up), r=(right, y), rd=(right, down), d=(x, down), ld=(left, down))
        surround = {}
        for key in iter_dict.keys():
            x_ord, y_ord = iter_dict[key]
            if self.check_valid_place(x_ord, y_ord):  # если в диапазоне, добавляем
                surround[key] = (x_ord,y_ord)
        for x_ord, y_ord in surround.values():  # теперь у нас есть координаты всех клеток окружения
            if my_board[x_ord][y_ord - 1] != EMPTY:  # то есть место не пустое, выходим
                return False
        return (x, y)  # Тест пройден

    def replace_obj_in_boards (self, dirty_board: dict, old: str, new: str) -> dict:
        '''Меняет во входящем словаре old на new'''
        clean_board = {}
        for key in dirty_board.keys():
            clean_board[key] = [' ' for _ in range(DEEP)]
            for space in range(DEEP):
                if dirty_board[key][space] == old:
                    clean_board[key][space] = new
                else:
                    clean_board[key][space] = dirty_board[key][space]
        return clean_board

    def show_users_boards (self):
        '''Показывает 1 или оба поля пользователя. Слева lazy_users_board или пустой, а второй генерится на основе my_board бота '''

        console = Console()
        table = Table(show_header=True, show_footer=True, box=box.ROUNDED, header_style="bold yellow",
                      footer_style="bold yellow", show_lines=True)
        # сначала делаем столбцы
        table.add_column(' ', style="bold yellow", width=2)  #для цифр
        for number in range(1072, ord(WIDTH) + 1):
            table.add_column(header=chr(number),footer=chr(number), width=1)
        table.add_column(' ', style="bold yellow", width=2)  # для цифр
        for number in range(1072, ord(WIDTH) + 1):
            table.add_column(header=chr(number),footer=chr(number), width=1)
        table.add_column(' ', style="bold yellow", width=2)  # для цифр
        table.add_column(header='Справка', width=40)  # для справки
        console.print(table)
        # теперь заполняем столбцы значениями
        if not self.lazy_user_board:  # если пользовательского поля нет, то показывается что набил уже бот
            left_board = self.enemy_board
        else:
            left_board = self.lazy_user_board
            # чтобы не загрязнять картинку поля чистим NOT_PERSPECTIVE
        left_board = self.replace_obj_in_boards(left_board,old=NOT_PERSPECTIVE,new=EMPTY)

        # создаем поле бота, заменяя все корабли и пусто на *
        right_board = self.replace_obj_in_boards(self.bot_board, old=SHIP, new=UNKNOWN)
        right_board = self.replace_obj_in_boards(right_board, old=EMPTY, new=UNKNOWN)
        right_board = self.replace_obj_in_boards(right_board, old=NOT_PERSPECTIVE, new=EMPTY)

        # создаем справку
        reference = {i:'' for i in range(DEEP + 1)}  # справка для символов
        reference[1] = f'{SHIP} = Корабль'
        reference[2] = f'{WOUND} = Раненый корабль'
        reference[3] = f'{KILL} = Убитый корабль'
        reference[4] = f'{MISSED} = Промах'
        reference[5] = f'{SHIP} = Целый корабль'
        reference[6] = f'{UNKNOWN} = Сюда еще не стреляли'
        reference[7] = f'{EMPTY} = Сюда можно и не стрелять'
        reference[8] = f'{SHIP} = {self.names_ships[1]}'
        reference[9] = f'{SHIP}{SHIP} = {self.names_ships[2]}'
        reference[10] = f'{SHIP}{SHIP}{SHIP} = {self.names_ships[3]}'

        # заполняем строки
        right_board = self.board_to_str(right_board)
        left_board = self.board_to_str(left_board)
        for number in range(1, DEEP + 1):
            left_line = left_board[number]
            right_line = right_board[number]
            table.add_row(str(number), *left_line, str(number), *right_line, str(number),reference[number])
        console.print(table)
        return (left_board, right_board)   # возврат пока только для тестирования

    def board_to_str(self, board):
        '''Транспонирует поле-словарь в {1:кортеж("симв","симв",...)}'''
        if board == {}:
            return False
        transposed_board = {}
        for number in range(DEEP):
            collect = []
            for n in range(1072, ord(WIDTH) + 1):
                char = chr(n)
                color_char = COLOR_SCHEME[board[char][number]] + board[char][number] + '[/' + COLOR_SCHEME[board[char][number]][1:]
                collect.append(color_char)
            transposed_board[number + 1] = tuple(collect) # храним с 1 ...
        return transposed_board

    def start_game(self, message):
        '''Начинает опрашивать игрока для настройки игры'''
        # самое самое начало игры, надо вывести правила
        self.stage = self.setup_game_step_1
        return 'Добро пожаловать в игру "Морской бой"!\nВыбери размер поля (ширину) в клетках от 2 до 32.'

    def setup_game_step_1(self, message):
        '''Выбор размера поля'''
        if not message.isdigit():  #Если это не цифра
            return 'Число, пожалуйста!'
        if int(message) < 2 or int(message) > 32 :
            return 'Выбери размер поля (ширину) в клетках от 2 до 32.'
        width = int(message)
        global WIDTH
        global DEEP
        DEEP = width
        WIDTH = chr(1071+width)
        line1 = f'Отлично! у нас будет поле: от "а" до "{WIDTH}" и от "1" до "{DEEP}":\n'
        line2 = 'Теперь выбери какие корабли будут и сколько штук.\n'
        line3 = ' Сначала количество, затем пробел, затем сколько палуб, и всё это через запятую.\n'
        line4 = 'Например, классический набор: 1 4, 2 3, 3 2, 4 1. Или набери "классика"'
        self.stage = self.setup_game_step_2
        return line1+line2+line3+line4

    def setup_game_step_2(self, message):
        '''Выбор количества кораблей'''
        if any([_ in message for _ in ['классика','класика', 'классический']]):
            message = '1 4, 2 3, 3 2, 4 1'
        array = message.split(',')  # список строк ['1 4', ' 2 3', ' 3 2', ' 4 1.']
        ships = []
        try:
            for line in array:
                amount, type_ship = re.findall('(\d+)\s(\d+)', line)[0]
                amount = int(amount)
                type_ship = int(type_ship)
                ships.append((amount,type_ship))  # должен получаться [(1,4), (2,3)]
                if amount < 1 or type_ship < 1:  # защита от кораблей 0 количества и 0 уровня
                    raise IndexError
        except IndexError:
            return 'Уточни список, я тебя не понял. Формат "1 4, 2 3, 3 2, 4 1"'
        ships_in_game = []
        for amount, type_ship in ships:
            for i in range(amount):
                ships_in_game.append(type_ship)  # должен собираться список [4, 4, 1, 1, 2, 3]
        line_ships, garbage = self.count_result_game(ships_in_game, {})  # составляю список кораблей
        line_ships = line_ships[10:] + '\n'  # отрезаем ненужную тут фразу
        if max(ships_in_game) > DEEP:  # защита от слишком длинных кораблей
            return f'{max(ships_in_game)}-палубник Не влезет на поле {DEEP}X{DEEP}! Уточни список. Формат "1 4, 2 3, 3 2, 4 1"'
        line_reference = ''
        for i in range(max(ships_in_game)):
            if i+1 in ships_in_game:
                line_reference += f'{self.names_ships[i + 1]} это {i + 1}-палубник\n'
        self.ships = ships_in_game [:]              # список кораблей для данной игры
        self.remaining_users_ships = self.ships[:]  # список вражеских кораблей для определения конца игры
        self.remaining_bots_ships = self.ships[:]   # список своих оставшихся в живых кораблей

        self.stage = self.setup_game_step_3
        return line_ships + line_reference + 'Всё верно?'

    def setup_game_step_3(self, message):
        '''Уточнение  правильности количества кораблей'''
        if any([_ in message for _ in ['нет','не']]):
            self.stage = self.setup_game_step_2
            return 'Уточни список. Формат "1 4, 2 3, 3 2, 4 1"'
        elif any([_ in message for _ in ['да', 'ага']]):
            self.stage = self.setup_game_step_4
            return 'Хочешь я нарисую поле за тебя и буду отслеживать свои попытки?'
        else:
            return 'Повтори, я тебя не понял'

    def setup_game_step_4(self, message):
        '''Генерация полей и выбор уровня сложности. self.who_is_answered отвечает за то, какая функция будет вызываться
        после попытки бота: либо ждём ответа от пользователя либо сами проверяем'''

        if any([_ in message for _ in ['нет', 'не']]):  # пользователь сам рисует поле.
            answer = 'Тогда расставляй корабли сам!\n' \
                     'Нельзя, чтобы корабли соприкасались ни боками, ни, даже, уголками.\n' \
                     'Как минимум одна клетка между ними должна быть обязательно.\n' \
                     'К краям поля корабли прижимать можно.\n' \
                     'Да, корабль - это клеточки идущие подряд, никаких изгибов не должно быть.\n' \
                    'Выбери уровень сложности (1 - простой, 2 - сложный, 3 - невозможный)'
        elif any([_ in message for _ in ['да', 'ага']]): # пять попыток сделать поле игроку
            for _ in range(5):
                try:
                    self.lazy_user_board, self.status_users_living_ships = self.create_board()
                except TimeoutError:
                    continue
                else:
                    break
            if not self.lazy_user_board:  # если так и не удалось сгенерировать поле
                self.stage = self.setup_game_step_2
                return 'Мне не удалось расставить такое количество кораблей, попробуй другой список судов. Формат "1 4, 2 3, 3 2, 4 1".'
        else:
            return 'Повтори, я тебя не понял.'

        # генерация поля бота
        for number in range(1072, ord(WIDTH) + 1):
            self.enemy_board[chr(number)] = ['*' for _ in range(DEEP)]
        for _ in range(5):  # пять попыток сделать поле боту
            try:
                self.bot_board, self.status_bots_living_ships = self.create_board()
            except TimeoutError:
                continue
            else:
                break
        if not self.bot_board:
            self.stage = self.setup_game_step_2
            return 'Мне не удалось расставить такое количество кораблей, попробуй другой список судов. Формат "1 4, 2 3, 3 2, 4 1".'

        # все генерации полей прошли удачно
        self.stage = self.setup_game_step_5
        return 'Выбери уровень сложности (1 - простой, 2 - сложный, 3 - невозможный)'

    def setup_game_step_5(self, message):
        '''Выбор уровня сложности'''
        answer = random.choice(['Начинай!','Твой выстрел!', 'Твой ход', 'Пли!'])
        if any([_ in message for _ in ['1', 'простой']]):  # базовый честный уровень сложности
            self.level = None
        elif any([_ in message for _ in ['2', 'сложный']]): # бот на удар в уже проверенную или бесполезную клетку отвечает мимо! todo добавить в этот и следующий уровень сложности удары по "квадратам"
            self.level = 2
        elif any([_ in message for _ in ['3', 'невозможный']]): # бот читерит, выдерживая один 1-палубный корабль, невыставленным, чтобы выставить только в самом крайнем случае, в самое последнее, оставшееся место
            self.level = 3
            self.cheat_list = self.cheat_bot_board()  #бот убирает 1 корабль и готовит список потенциальных мест
            log.info(f'Cheat mode on. Potential places are {self.cheat_list}')
        else:
            return 'Не понял!'
        self.stage = self.check_hit_on_bot_board
        return answer

    def run(self, message: str):
        '''Сообщение от игрока, которое надо обработать в зависимости от текущей ситуации
           предположим мы будем хранить текущее состояние в отдельной переменной'''
        message = message.lower()

        # Обработка команд боту
        try:  #обработка команд может быть только в игре, но не при старте, при старте будет вываливаться ошибка
            if any([_ in message for _ in ['выход','выйти','конец','надоел','сдаюсь']]):
                answer = self.result_game()
                return answer
            elif any([_ in message for _ in ['сохрани']]):
                bots_ships, bots_score = self.count_result_game(self.remaining_bots_ships, self.bot_board)
                user_ships, users_score = self.count_result_game(self.remaining_users_ships, self.lazy_user_board)
                answer = f'У меня {bots_ships}\nУ тебя {user_ships}\nСчёт: {bots_score} - {users_score}.\nСохраняю игру!'
                self.message_after_load = answer.replace('Сохраняю игру', 'Твой ход')  # с этого сообщения бот начнёт сохранённую игру
                return answer
            elif any([_ in message for _ in ['покажи', 'показать']]):  # проверка показ полей
                self.show_users_boards()
                return 'Океюшки'
            elif any([_ in message for _ in ['показывай поле каждый ход', 'каждый ход']]):
                self.show_every_turn = True
                return 'Океюшки'
            elif any([_ in message for _ in ['помощь', 'помошь', 'помоги', 'хелп']]):
                return 'Чтобы выйти, набери "выход".\nЧтобы получить список сохравнишхся в живых кораблей, набери "корабли"\nЧтобы увидеть свои поля, набери "покажи"'
            elif any([_ in message for _ in ['корабли', 'какие', 'сколько', 'кораблей', 'какой', 'счёт']]):
                bots_ships, bots_score = self.count_result_game(self.remaining_bots_ships, self.bot_board)
                user_ships, users_score = self.count_result_game(self.remaining_users_ships, self.lazy_user_board)
                return f'У меня {bots_ships}\nУ тебя {user_ships}\nСчёт: {bots_score} - {users_score}'
        except Exception:
            return 'Не понял'

        answer = self.stage(message)    # основная часть работы, в переменной хранится соответствующая функция
        if self.show_every_turn:        # показ поля в терминале
            self.show_users_boards()
        return answer

    def check_lazy_users_board(self, answer: str) -> str:
        '''Проверяет за игрока, попал ли бот, и дополняет ответ, пока бот не промахнётся'''

        while True:
            x,y = self.previously_bot_turn
            if self.lazy_user_board[x][y-1] == SHIP:
                place = x + ' ' + str(y)
                phrase_lazy_user = self.check_killing_ship(place=place,board=self.lazy_user_board,status=self.status_users_living_ships, ships=self.remaining_users_ships)
                answer += '\n' + phrase_lazy_user + '\n' + self.user_reply_about_bot_turn(phrase_lazy_user)
            elif self.lazy_user_board[x][y-1] == EMPTY:
                phrase_lazy_user = 'Ч**т! Мимо!'
                self.lazy_user_board[x][y - 1] = MISSED
                self.stage = self.check_hit_on_bot_board
                reply = self.user_reply_about_bot_turn(phrase_lazy_user)
                return answer + '\n' + phrase_lazy_user + reply
            elif not self.remaining_users_ships: #  проверка в конце игры
                self.stage = 'end the game'
                return answer
            else:
                raise TypeError(f'Что-то неправильное в поиске целей у бота. Он выбрал {self.lazy_user_board[x][y-1]}')

    def cheat_mode(self,turn: str, x: str, y: int) -> str:
        '''Работа с кораблём-призраком в режиме сложности 3'''

        answer = ''
        # чтобы не казалось, что бот жульничает, иногда 50% он сдает корабль призрак предпоследним
        if len(self.cheat_list) == 2 and (x, y) in self.cheat_list and random.choice([True, False]):
            log.info(
                f'cheat mode off. Unfortunately, not last place ({x},{y}) is removing from {self.cheat_list}, but it is the fatum!')
            self.bot_board[x][y - 1] == SHIP
            self.cheat_list = []
            self.status_bots_living_ships[self.cheat_number]['place'] = [(x, y)]
            answer = self.check_killing_ship(place=turn, board=self.bot_board,
                                             status=self.status_bots_living_ships,
                                             ships=self.remaining_bots_ships)
        # есть еще места для корабля призрака и это одно из этих мест
        elif len(self.cheat_list) > 1 and (x, y) in self.cheat_list:
            log.info(f'run cheat mode. remove ({x},{y}) from {self.cheat_list}')
            self.cheat_list.remove((x, y))  # просто удаляем из списка потенциальных мест корабля-призрака
            answer = False
        # всё, увиливать дальше некуда, то ставим корабль и говорим, что попал
        elif len(self.cheat_list) == 1 and (x, y) in self.cheat_list:
            log.info(f'cheat mode off. All places are over! last place ({x},{y}) is removing from {self.cheat_list}')
            self.bot_board[x][y - 1] == SHIP
            self.cheat_list = []
            self.status_bots_living_ships[self.cheat_number]['place'] = [(x, y)]
            answer = self.check_killing_ship(place=turn, board=self.bot_board,
                                             status=self.status_bots_living_ships,
                                             ships=self.remaining_bots_ships)
        return answer

    def check_hit_on_bot_board(self, turn: str) -> str:
        '''Проверяет попал ли игрок. Возвращает ответ и ставит stage в зависимости от результата.'''

        if not (turn := self.check_phrase_about_try(turn)):  # проверяет валидность хода игрока, стандартизируя его ответ
            return 'Не понял'

        #Теперь проверяем куда ударил игрок
        x, y = self.refactor(turn)
        if self.bot_board[x][y - 1] == EMPTY:      # промах
            if self.level == 3:                     # cheat_mode on
                if (answer := self.cheat_mode(turn, x, y)):
                    return answer
            # обычная обработка без читов и при большом списке с читами
            self.bot_board[x][y - 1] = MISSED
            bot_turn = self.bot_turn()
            answer = f'Мимо!\nМой ход: {bot_turn}'
            self.stage = self.user_reply_about_bot_turn  # ждём ответа от пользователя попал или мимо
            if self.lazy_user_board:  # если мы проверяем за пользователя, то обрабатываем сами, пока не промахнемся
                answer = self.check_lazy_users_board(answer)
                self.stage = self.check_hit_on_bot_board  # ждём ответа от пользователя куда теперь он бьет

        elif self.bot_board[x][y - 1] == SHIP:  # попал, проверка на целостность всего корабля
            answer = self.check_killing_ship(place=turn, board=self.bot_board, status=self.status_bots_living_ships, ships=self.remaining_bots_ships)

        else: # wound, kill, missed или not_perspective, то есть ход глупый
            if not self.level:                          # уровень сложности 0
                answer = 'Уже было, давай другое место!'
                self.stage = self.check_hit_on_bot_board
            else:                                       # уровень сложности 1,2...
                bot_turn = self.bot_turn()  # ход бота
                answer = f'Мимо!\nМой ход: {bot_turn}'
                self.stage = self.user_reply_about_bot_turn  # ждём ответа от пользователя попал или мимо
                if self.lazy_user_board:  # если мы проверяем за пользователя, то обрабатываем сами, пока не промахнемся
                    self.stage = self.check_hit_on_bot_board  # ждём ответа от пользователя куда теперь он бьет
                    answer = self.check_lazy_users_board(answer)  # если корабли кончились тут проставится нужный флаг
        return answer

    def bot_turn(self):
        '''Игрок промахнулся, бот отвечает строкой вида "а 1" '''
        if self.assuming_hit:  #если у бота уже есть вариант выстрела
            x, y = self.assuming_hit.pop(0)
            bot_turn = x +' ' + str(y)
            self.previously_bot_turn = (x,y)  # кортеж для хранения хода бота, чтобы занести результат после ответа игрока
        else:
            variants = []  # список потенциальных вариантов для рандомного выбора
            for key in self.enemy_board.keys():
                index = 0
                for row in self.enemy_board[key]:
                    if row == UNKNOWN:
                        x = key
                        y = index
                        variants.append((x,y+1))
                    index += 1
            if len(variants) < (sum(self.remaining_users_ships) - self.status_users_ship['hits']): # если у противника больше кораблей, чем мест
                bot_turn = 'Да ты похоже жульничаешь. Я так не играю!'
                return bot_turn
            x, y = random.choice(variants)
            bot_turn = x + ' ' + str(y)
            self.previously_bot_turn = (x,y)
        return bot_turn

    def check_killing_ship(self, place: str, board: dict, status: dict, ships: list) -> str:
        '''Проверка ранил игрок/бот или убил корабль, а также обработка поля, словаря и списка кораблей
        В этой функции обрабатывается как действия юзера, так и действия с автоматическим ответом за юзера ботом'''
        x, y = self.refactor(place)
        for key, value in status.items(): # это dict(1: dict(hits=4, place=[('a',1),('a',2),('a',3),('a',4)]))
            for x_ord, y_ord in value['place']:
                if x_ord == x and y_ord == y:  # мы его нашли
                    search = key  # номер корабля, который мы потенциально ищем, куда попали, мы его обязательно должны найти
        if status[search]['hits'] == 1:  # то есть осталась одна жизнь, а значит мы его убили
            answer = 'Убил!'
            self.filling_not_perspective(status[search], board=board) # заменяем клетки корабля на KILL и вокруг
            if board == self.lazy_user_board:  # если мы обрабатываем попадания бота во вражеский корабль, а иначе бот обнуляет свой список при убийстве его кораблей игроком, функция то общая
                self.assuming_hit = []  # обнуляем список перспективных целей бота
            decks = len(status[search]['place'])  # кол-во палуб исходного корабля
            ships.remove(decks)  # удаляем из списка кораблей
            del status[search]  # убираем корабль из списка словарей
            if not status: # проверка есть ли вообще корабли, оставшиеся в живых?
                answer = 'Потопил!\n' + self.result_game()
                return answer
        else:
            answer = 'Ранил!'
            status[search]['hits'] -= 1 # вычитаем одну жизнь
            board[x][y-1] = WOUND

        self.stage = self.check_hit_on_bot_board
        return answer

    def user_reply_about_bot_turn(self, reply: str) -> str:
        '''Здесь Обрабатывается ответ игрока, ведущего своё поле, на наш зависимости от результата.
        Оно дублируется с check_killing_ship, для чего надо поставить костыль
        Также выдает ответ строкой. Если мы попали, сразу дает следующий ход в той же строке'''
        reply = reply.lower()
        x,y = self.previously_bot_turn
        log.debug(f'Список перспективных целей бота in user_reply= {self.assuming_hit}')
        if 'попал' in reply or 'ранил' in reply:
            self.enemy_board[x][y - 1] = WOUND  # надо записать в поле проверок, очертить круг вариантов и выдать еще один удар
            self.status_users_ship['hits'] += 1  # ведем словарь жертвы типа {hits=2, place=[('a',1),('b',2)]} для обработки, где hits это не жизни, а удары
            self.status_users_ship['place'].append((x, y))
            self.assuming_hit = self.search_variants_for_hit_wounded_ships(x, y, self.assuming_hit)  # обновляем список перспективных целей
            bot_turn = self.bot_turn()
            answer = random.choice(['Отлично!','Врагу не сдается ваш гордый Варяг!','Ха!','Иллитидская сила!','Прямой наводкой!','Ура!']) + \
                     '\n' + random.choice(['Теперь','А мы вот так','Сейчас','Попробую','Эээ']) + ': ' + bot_turn
            self.stage = self.check_hit_on_bot_board
        elif 'убил' in reply or 'прикончил' in reply:  # надо записать в поле проверок и выдать еще один удар
            self.status_users_ship['hits'] += 1
            self.status_users_ship['place'].append((x,y))
            if not self.lazy_user_board:  # Костыль, чтобы убрать дублируемость с check_killing_ship
                if self.status_users_ship['hits'] in self.remaining_users_ships:  # в списке есть корабль
                    self.remaining_users_ships.remove(self.status_users_ship['hits'])
                else:
                    return ('Да ты похоже жульничаешь. Я так не играю!','end the game')
            self.filling_not_perspective(self.status_users_ship, board=self.enemy_board)  #там заполняется места убитого корабля на KILL, а вокруг ставятся флаги NOT_PERSPECTIVE
            self.status_users_ship['hits'] = 0  # обнуляем словарь для следующей жертвы
            self.status_users_ship['place'] = []
            if not self.remaining_users_ships:  # у противника кончились корабли, конец игры
                # if self.lazy_user_board:  # Если бот сам проверяет, то ответ на конец уже есть
                #     return ''
                answer = self.result_game()
                self.assuming_hit = []  # обнуляем список перспективных целей, их больше нет
                return answer
            bot_turn = self.bot_turn()
            answer = random.choice(['Вот так!','Получай!','На!','***!','Так тебе!','Вооо!']) + ' : ' + bot_turn
            self.stage = self.check_hit_on_bot_board
        elif 'мимо' in reply or 'промазал' in reply:
            self.enemy_board[x][y - 1] = MISSED # надо записать в поле проверок и предложить юзеру сделать ход
            answer = random.choice(['Ясненько!','Жаль!','Эээх!','***!','Упс!','Тааак!']) + ' ' + random.choice(['Твой ход.','Ходи.','Стреляй.','Шмаляй.','Прицелься получше.','Давай.','Пробуй.'])
            self.check_hit_on_bot_board
        elif 'вот и кончилась наша' in reply:
            self.stage = 'end the game'
            return ''
        else:
            answer = 'Эээ, не понял. Повтори!'
        return answer

    def refactor(self, phrase: str):
        '''превращает строку вида 'а 1' в кортеж из ('a', 1)'''
        x, y = phrase.split(' ')
        y = int(y)
        return (x,y)

    def filling_not_perspective(self, status_users_ship: dict, board: dict):
        '''Заполняет поля убитого корабля KILL, вокруг него выставляет NOT_PERSPECTIVE по словарю {hits=2, place=[('a',1),('b',2)]}
        Поле передается для универсализации функции для обоих игроков'''
        for x,y in status_users_ship['place']:              # проходим по всем точкам корабля
            board[x][y - 1] = KILL                # заполняем все клетки корабля "убитый"
            surround = self.search_full_surround(x, y)
            for x_ord, y_ord in surround.values():          # проходим по окружению точки корабля, уменьшая поле действий
                if board[x_ord][y_ord - 1] == UNKNOWN or board[x_ord][y_ord - 1] == EMPTY:
                    board[x_ord][y_ord - 1] = NOT_PERSPECTIVE
        return

    def search_variants_for_hit_wounded_ships(self, x: str, y: int, old_assuming_hit: list):
        '''Дополняет и возвращает список кортежей боту для более точного поиска и добивания корабля противника'''
        assuming_hit = old_assuming_hit[:]
        log.debug(f'Список перспективных целей бота в начале поиска перспективных целей = {assuming_hit}')
        surround = self.search_ortogonal_surround(x, y)  # определяем окружение
        perspective_direction = []
        for x_ord, y_ord in surround.values():   # ищем вокруг точки раненых
            if self.enemy_board[x_ord][y_ord - 1] == WOUND:
                perspective_direction.append((x_ord,y_ord))
        for x_ord, y_ord in surround.values():  # проходимся по окружению на случай если раненых не найдено (1 удар по х-палубному кораблю)
                if self.enemy_board[x_ord][y_ord - 1] == UNKNOWN and not perspective_direction: #если перспективного направления не найдено, то просто ищем по UNKNOWN
                    assuming_hit.append((x_ord,y_ord))

        if len(perspective_direction) == 1:  # если найдено только 1 перспективное направление, то надо проверить на * и противоположное
            x_shift = ord(x) - ord(perspective_direction[0][0]) # меняем местами обычный порядок вычитаемых
            y_shift = y - perspective_direction[0][1]
            x_new = chr(ord(x) + x_shift)
            y_new = y + y_shift
            if self.check_valid_place(x=x_new,y=y_new):  # если не промахнулись мимо поля
                if self.enemy_board[x_new][y_new - 1] == UNKNOWN:
                    assuming_hit.append((x_new, y_new))  #  если там неизвестность, то добавляем к списку потенциальных

        for x_ord, y_ord in perspective_direction:  # при пустом списке просто не запустится рекурсивный поиск по концам
            x_shift = ord(x_ord) - ord(x)
            y_shift = y_ord - y
            matrix_movement = (x_shift,y_shift)
            #orto_matrix1 = (y_shift,x_shift)  ортогональные и неперспективные относительно перспективного движения
            #orto_matrix2 = (-1 * y_shift,-1 * x_shift)  направления, матрицы просто для большего понимания строчки внизу
            not_perspective_places = [(chr(ord(x_ord) + y_shift),y_ord + x_shift), (chr(ord(x_ord) - y_shift),y_ord - x_shift)]  #эти две бесперспективные точки
            for place in not_perspective_places:  # проходим по списку и проверяем их в списке потенциальных целей
                if place in assuming_hit:         # и если они там есть просто удаляем их из списка потенц. целей
                    assuming_hit.remove(place)
            if result := self.recourse_search(x=x_ord, y=y_ord,matrix_movement=matrix_movement):  # поиск концов
                assuming_hit.append(result)
        set_list = set(assuming_hit)    # убираем возможные дубляжи точек
        assuming_hit = list(set_list)
        log.debug(f'Список перспективных целей бота в конце поиска перспективных целей = {assuming_hit}')
        return assuming_hit

    def recourse_search(self, x: str, y: int, matrix_movement: tuple):
        '''двигается рекурсивно в сторону матрицы движения, проверяя наличие WOUND'''
        x_shift, y_shift = matrix_movement
        x_new = chr(ord(x) + x_shift)
        y_new = y + y_shift
        if not self.check_valid_place(x=x_new, y=y_new):  # если мы вышли за поле
            return False
        if self.enemy_board[x_new][y_new - 1] == WOUND:
            result = self.recourse_search(x=x_new, y=y_new, matrix_movement=matrix_movement)
            return result
        elif self.enemy_board[x_new][y_new - 1] == UNKNOWN:
            return (x_new,y_new)
        return False

    def search_ortogonal_surround(self, x: str, y: int) -> dict:
        '''Составление словаря ортогонального окружения точки'''
        full_surround = self.search_full_surround(x=x,y=y)
        surround = {key: full_surround[key] for key in full_surround.keys() if len(key)==1}
        return surround

    def search_full_surround(self, x: str, y: int)-> dict:
        '''Составление словаря полного окружения точки'''
        left = chr(ord(x) - 1);
        right = chr(ord(x) + 1);
        up = y - 1;
        down = y + 1
        iter_dict = dict(l=(left, y), lu=(left, up), u=(x, up), ru=(right, up), r=(right, y), rd=(right, down),
                         d=(x, down), ld=(left, down))
        surround = {}
        for key in iter_dict.keys():
            x_ord, y_ord = iter_dict[key]
            if self.check_valid_place(x_ord, y_ord):  # если в диапазоне, добавляем
                surround[key] = (x_ord, y_ord)
        return surround

    def check_valid_place(self, x: str, y: int):
        '''Обрабатывает валидность точки в рамках поля. Если выходит, выдает False, при норме выдает True'''
        return not (ord(x) < 1072 or ord(x) > ord(WIDTH) or y < 1 or y > DEEP)

    def check_phrase_about_try(self, phrase: str):
        '''Обрабатывает ответ игрока на валидность попытки. Если бот не понял, выдает False, если понял, то приводит к стандартному виду и отдает строкой'''
        unity_phrase = False  # по умолчанию бот не понял
        phrase = phrase.lower()
        phrase = phrase.replace(' ','')  # убираем
        if len(phrase) < 2:  # Значит точно неверный ответ
            return False
        x = phrase[0]
        phrase = phrase[1:]  # убираем первую букву, должна остаться цифра
        try:
            y = int(phrase)
        except:
            return False
        if not self.check_valid_place(x, y):  # выпало за диапазон
            return False
        unity_phrase = x + ' ' + str(y) #все проверки пройдены, формат ответа 'а 1' оба поля разделены пробелом и в нижнем регистре
        return unity_phrase

    def result_game(self) -> str:
        '''Вычисляет ответ юзеру при окончании игры из игры'''

        bots_ships, bots_score = self.count_result_game(self.remaining_bots_ships, self.bot_board)
        user_ships, users_score = self.count_result_game(self.remaining_users_ships, self.lazy_user_board)
        if bots_score > users_score:
            winner = f'Моя победа по очкам: {bots_score} против {users_score}'
        elif bots_score == users_score:
            winner = f'По очкам ничья. {bots_score} и {users_score}'
        else:
            winner = f'Твоя победа по очкам: {users_score} против {bots_score}'
        if bots_score == 0:
            winner = 'Ты потопил все мои корабли!'
        if users_score == 0:
            winner = 'Я потопил все твои корабли!'
        self.stage = 'end the game'
        return f'Вот и кончилась наша игра.\n{winner}\nУ меня {bots_ships}.\nУ тебя {user_ships}.'

    def count_result_game(self, ships: list, board: dict) -> tuple:
        '''Вычисляет по окончании игры оставшиеся корабли и выдает строку и сумму палуб выживших судов'''

        remaining_ships = 'осталось: ' #
        dict_ships = {x:0 for x in ships}   # собираем словарь из уникальных типов кораблей
        for ship in ships:                  # подсчитываем количество каждого типа
            dict_ships[ship] += 1
        dict_endings = {x:'' for x in ships}  # строим словарь окончаний для числительных
        for decks, amount in dict_ships.items():
            if 5 > amount > 1:
                dict_endings[decks] = 'а'
            elif amount > 4:
                dict_endings[decks] = 'ов'
        for decks, amount in dict_ships.items():
            remaining_ships += str(amount) + ' ' + self.names_ships[decks] + dict_endings[decks] + ', '
        if remaining_ships != 'осталось: ':
            remaining_ships = remaining_ships[:-2]  #отрезаем последние 2 лишних символа
        else:
            remaining_ships = 'кораблей то и не осталось'
        # Подсчёт очков
        surviving_part_of_ships = 0
        if board:
            for line in board.values():
                for field in line:
                    if field == SHIP:
                        surviving_part_of_ships += 1
        else:  #значит юзер сам вёл поле, поэтому подсчёт посложнее.
            remaining_users_ships = sum(ships)  # сколько осталось кораблей у пользователя
            correct = self.status_users_ship['hits']  # дает поправку на раненный корабль из списка выше
            surviving_part_of_ships = remaining_users_ships - correct

        if self.cheat_list and board == self.bot_board:  # если список мест для корабля-призрака не пустой, значит
            surviving_part_of_ships += 1                 # добавить + 1 к очкам, а не то, бот палится, что одного корабля нету :)

        return (remaining_ships, surviving_part_of_ships)

if __name__ == '__main__':
    game = SeaBattle(395305264)
    answer = game.run('')
    print(answer)
    while True:
        if game.stage == 'end the game':
            break
        message = input('Твой ход: ')
        answer = game.run(message)
        print(answer)

























