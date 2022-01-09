'''Модуль обработки текстовых сценариев согласно словарям в settings.py
Игра или сценарий:
    1. Должна быть сделана на классе.
    2. В классе должна иметь функцию run, которая принимает текстовую строку и отдает текстовую строку ответа.
    3. Должна иметь атрибут stage для сверки состояния игры.
    4. конец игры должен характеризоваться атрибутом stage = 'end the game'.
    5. Сохранение игры осуществляется посредством передачи в ответе ключевых слов в любом месте "Сохраняю игру".
    6. Сохранение игры осуществляется за счёт сохранения экземпляра, загрузка обратна.
    7. Сохраняемый экземпляр должен иметь атрибут message_after_load: str, который будет выдан юзеру после загрузки.
'''

import logging
import settings
import bots_handlers

log = logging.getLogger('scenarios')
fh = logging.FileHandler("log/scenarios.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)
log.setLevel(logging.DEBUG)

class Scenarios:

    def __init__(self, user, scenario: str):
        self.id = user.id
        self.user = user  # сохраняем экземпляр пользователя
        self.stage = 'start'
        self.scenario = scenario  # переменная хранящая название соответствующего сценария

    def run(self, message):
        '''Обработка сценария'''

        if any([_ in message for _ in ['выйти','нет','выход','уйти','уйди', 'выйди']]):
            self.stage = 'end the game'  # конец сценария
            return 'Не очень то и хотелось!'

        steps = settings.SCENARIOS[self.scenario]['steps']
        if self.stage == 'start':                       # начало сценария
            answer = steps['step 1']['text']
            self.user.state = 'step 1'
            self.stage = 'continue'
        else:                                           # Продолжение сценария
            step = steps[self.user.state]
            handler = getattr(bots_handlers,step['handler'])
            if handler(message, context=self.user.context):
                next_step = step['next step']
                answer = steps[next_step]['text'].format(**self.user.context)
                self.user.state = next_step
                if not steps[next_step]['next step']:   # если шаг последний
                    self.stage = 'end the game'         # конец сценария
            else:
                answer = step['fault']
        return answer


