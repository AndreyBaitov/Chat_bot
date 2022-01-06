import random
from random import randint
from parser_name_from_vk import NameParser

class BullsCows:

    def __init__(self, id: int):
        self.id = id
        url = 'https://vk.com/id' + str(id)
        user = NameParser(url)
        self.user_name = user.parse_name_user()  #добавляет имя игрока к экземпляру для бота
        self.stage = self.start_game

    def check_input(self,message) -> str:
        try:
            number = int(message)
            if len(message) != len(self.cypher):
                raise NameError
            return True
        except (NameError, ValueError):
            return False

    def run(self, message):
        '''Обработка сообщений пользователя'''
        if any([_ in message for _ in ['не', 'нет', 'выход', 'выйти']]):
            answer = 'Пока, пока, ' + random.choice(
                ['хакер', 'ковбой', 'ха**р', 'ков**й', 'математик', 'медвежатник']) + '!'
            self.stage = 'stop game'
        else:
            answer = self.stage(message)
        return answer

    def start_game(self, message: str) -> str:
        '''Подготовка к игре'''
        self.stage = self.generation_number
        greetings = 'Добро пожаловать в игру Быки и коровы.\n'
        rules = 'Жирная цифра "𝟏" = число угадано на верной позиции\n' + 'Пустая цифра "𝟙" = число угадано на неверной позиции\n'
        question = 'Выбери длину шифра от 1 до 9'
        return greetings + rules + question

    def generation_number(self, amount: str) -> str:
        '''Генерируем загаданное число, возвращает либо False, либо строку'''
        try:
            amount = int(amount)
        except Exception:
            return 'Число, пожалуйста!'
        if not (1 < amount < 10): return 'От 1 до 9, пожалуйста!'
        numbers = [x for x in range(1,10)]
        cypher = ''
        for x in range(amount):
            l = random.choice(numbers)
            numbers.remove(l)
            cypher += str(l)
        self.cypher = cypher  # сохраняем загаданный код
        self.stage = self.check_trial
        return '* '* len(cypher)

    def check_trial(self, message: str) -> str:
        if message == self.cypher:  # игрок угадал
            self.stage = self.end_game
            return 'Угадал!\nХочешь ещё?'
        if not self.check_input(message):
            return f'Введи нужное количество цифр: {len(self.cypher)}'
        answer = ''
        for i in range(len(self.cypher)):
            if message[i] == self.cypher[i]:                # угадал = жирная цифра
                answer += chr(120783 + ord(message[i])-49)
            elif message[i] in self.cypher:                 # почти угадал = бледная цифра
                answer += chr(120793 + ord(message[i]) - 49)
            else:
                answer += message[i] + chr(822)             # '1' + chr(822) символ зачеркивания
        return answer

    def end_game(self, message: str) -> str:
        '''Обработать выход или повторную игру'''
        if any([_ in message for _ in ['да','ага','ещё','угу']]):
            answer = self.start_game('')
        elif any([_ in message for _ in ['не', 'нет', 'выход', 'выйти']]):
            answer = 'Пока, пока, ' + random.choice(['хакер','ковбой','ха**р','ков**й','математик','медвежатник'])+ '!'
            self.stage = 'stop game'
        return answer

if __name__ == '__main__':
    game = BullsCows(id=395305264)
    answer = game.run('123')
    while True:
        print(answer)
        message = input('Твой ответ:')
        answer = game.run(message)
        if 'Пока, пока' in answer:
            print(answer)
            break  #игра окончена, бот сдался
