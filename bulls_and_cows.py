import random
from random import randint

class BullsCows:

    def __init__(self, user):
        self.id = user.id
        self.user = user  # сохраняем экземпляр пользователя
        self.stage = self.start_game

    def check_input(self,message) -> str:
        '''Проверка сообщения игрока на валидность: цифры и количество символов'''
        try:
            number = int(message)
            if len(message) != len(self.cypher):
                raise NameError
            return True
        except (NameError, ValueError):
            return False

    def run(self, message):
        '''Обработка сообщения пользователя: на выход или согласно этапу(в переменной хранится функция)'''
        if any([_ in message for _ in ['не', 'нет', 'выход', 'выйти']]):
            answer = 'Пока, пока, ' + random.choice(
                ['хакер', 'ковбой', 'ха**р', 'ков**й', 'математик', 'медвежатник']) + '!'
            self.stage = 'end the game'
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
        '''Генерация загаданного числа и обработка несоотвествующих выборов'''
        try:
            amount = int(amount)
        except Exception:
            return 'Число, пожалуйста!'
        if not (0 < amount < 10): return 'От 1 до 9, пожалуйста!'
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
        '''Обработка ответа игрока в игре'''
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
        '''Выбор игрока выйти или повторить'''
        if any([_ in message for _ in ['да','ага','ещё','угу','повтор']]):
            answer = self.start_game('')
        elif any([_ in message for _ in ['не', 'нет', 'выход', 'выйти']]):
            answer = 'Пока, пока, ' + random.choice(['хакер','ковбой','ха**р','ков**й','математик','медвежатник'])+ '!'
            self.stage = 'end the game'
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
