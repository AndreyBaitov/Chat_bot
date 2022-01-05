'''Игра города для бота
можно добавить функцию сохранения данных юзера с игрой в самом боте в виде сохранения объекта GameTowns
Игуату почему то на и надо отвечать
'''

import logging, random, time
from parser_name_from_vk import NameParser


log = logging.getLogger('Game_towns')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("log/game_towns.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

import re, os
import json

class GameTowns:

    def __init__(self, id):
        self.id = id
        self.list_choosed_towns = []
        self.list_towns = self.create_list_towns()
        self.time = time.time()  # переменная, где хранится время последнего ответа для определения не надоело ли игроку
        self.count_wrong_answers = 0
        url = 'https://vk.com/id' + str(id)
        user = NameParser(url)
        self.user_name = user.parse_name_user()  #добавляет имя игрока к экземпляру для бота

    def create_list_towns(self):
        with open('resources/towns/cities.json', 'r', encoding='utf-8') as file:  # основной список городов 10 тыс
            json_data = json.load(file)
        json_dict = json_data['city']
        set_towns = set()
        for obj in json_dict:
            set_towns.add(obj['name'])
        with open('resources/towns/goroda.txt', 'r', encoding='cp1251') as file:  # дополняем из второго списка городов
            for town in file:  # там есть повторяющиеся около 800, есть около 200 неповторяющихся
                town = town.rstrip()
                if not town:  # если строка пустая
                    continue
                if town in set_towns:  # если такой город уже есть
                    continue
                set_towns.add(town)  # если все проверки пройдены, добавляем
        list_towns = list(set_towns)  # превращаем в список
        return list_towns

    def game(self, town: str ='Москва'):
        '''Непосредственно проверка города и выдача ответа в виде строки'''
        self.time = time.time()  #обновляем переменную времени общения вне зависимости от ответа. Скуку проверяет бот
        town = town.lower()   #все в строчный регистр, чтобы упростить проверку команд
        if any([_ in town for _ in ['сохрани','сейв','запомни']]):  #пользователь хочет сохранить игру
            ending = self.choose_end_char_number(len(self.list_choosed_towns))
            reply = f'Сохраняю игру, чтобы продолжить, начни игру заново. Мы уже назвали {len(self.list_choosed_towns)} город{ending}'
            return reply                                    # бот должен сохранить игру по ключу сохраняю игру!
        if any([_ in town for _ in ['надоело','устал','выход','выйти']]):  #пользователь хочет закончить
            ending = self.choose_end_char_number(len(self.list_choosed_towns))
            reply = f'Что ж, похоже я выиграл! Вместе мы назвали {len(self.list_choosed_towns)} город{ending}'  # конец игры
            return reply                                    # бот должен закончить игру по ключу похоже я выиграл!...
        if town == 'да' or town == 'ага' or any([_ in town for _ in ['подскаж','подсказк','помог']]):  #пользователь просит помощи
            reply = self.prompt()
            return reply                                # бот дает подсказку, не обновляя списки
        town = town.title()                         # Приведение ответа в приемлемый вид, как в словаре с заглавными
        if town in self.list_choosed_towns:             #город уже есть в списке
            adding = self.check_numbers_wrong_answers()   # проверяет сколько уже было неправильных ответов
            return 'Такой город уже был' + adding       # Если ответов еще мало, то adding=''
        if town not in self.list_towns:                 #Бот не знает такого города
            adding = self.check_numbers_wrong_answers()
            return 'Я не знаю такого города!' + adding
        if self.list_choosed_towns != []:  #игра не началась только что, а значит надо проверить на соответствие города бота
            end_char = self.list_choosed_towns[-1][-1]
            forward_char = town[0].lower()
            if forward_char != end_char:                    # ответ неправильный
                adding = self.check_numbers_wrong_answers()
                return f'Не подходит!, надо на {end_char}{adding}'
        self.list_choosed_towns.append(town)        # Все проверки пройдены. Вносим в список
        reply = self.search_town(town)  #  Теперь ищем ответ
        if reply == 'Я проиграл!':
            ending = self.choose_end_char_number(len(self.list_choosed_towns))
            reply = f'Горе мне, я проиграл! Вместе мы назвали {len(self.list_choosed_towns)} город{ending}'  # конец игры
            return reply  # бот должен закончить игру по ключу Горе мне...
        self.list_choosed_towns.append(reply)  #Вставляем ответ в список
        return reply

    def search_town(self, town: str):
        '''Поиск подходящего города и выдача его из рандомного списка'''
        reply = 'Я проиграл!'
        end_char = town[-1]  # на что заканчивается город игрока
        if any([_ in end_char for _ in ['ь','ъ','ы']]):
            end_char = town[-2]
        if any([_ in end_char for _ in ['ь','ъ','ы']]):  # на всякий случай проверим и еще один раз
            end_char = town[-3]
        acceptable_towns = []
        for city in self.list_towns:
            forward_char = city[0].lower()
            if forward_char == end_char:
                acceptable_towns.append(city)
        if acceptable_towns == []:
            return reply
        reply = random.choice(acceptable_towns)
        return reply

    def choose_end_char_number(self, number: int):
        if 10 <= number <= 20:
            return 'ов'  # 10-20 городов
        number = str(number)
        if number[-1] == '1':
            return ''  # 1,21,31 город
        elif number[-1] == '2' or number[-1] == '3' or number[-1] == '4':
            return 'а'  # 2,22,32 города
        else:
            return 'ов'  # 5,36,47,48,49 городов
        return 'ов'  # на всякий случай

    def prompt(self):
        '''функция подсказки пользователю варианта ответа'''
        town = self.list_choosed_towns[-1]  #Смотрим, какой город последний
        reply = self.search_town(town)  # Теперь ищем ответ своей же функцией
        if reply == 'Я проиграл!':
            return 'Похоже, нет такого города! Горе мне!'
        reply = 'Подсказываю, ' + reply
        return reply

    def check_numbers_wrong_answers(self):
        '''функция следящая за тем, сколько неправильных ответов дал пользователь'''
        adding = ''
        self.count_wrong_answers += 1
        if self.count_wrong_answers > 3:  # Если уже 3 неправильных ответа
            adding = '. Подсказать?'
            self.count_wrong_answers = 0
        return adding  #Строка добавляющая либо '' к ответу на неправильный ответ, либо вопрос подсказать?

if __name__ == '__main__':
    id = 395305264
    game = GameTowns(id)  #395305264 - мой
    if game.__class__ == GameTowns:
        print('yeap')
    print('Добро пожаловать в игру Города, назови свой первый город')
    while True:
        town = input('Твой ответ:')
        reply = game.game(town)
        if 'Горе мне' in reply or 'похоже я выиграл!' in reply:
            print(reply)
            break  #игра окончена, бот сдался
        print(reply)

