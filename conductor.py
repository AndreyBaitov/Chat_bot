'''for Python 3.10
Организация словарей в список, сами словари сортируютя по количеству слов в них Dict1 = {'хуй':'**й'},Dict2 = {'На хуй':'На ***й'},{'на хуй':'на ***й'} подумать как автоматизировать первую букву
Неизвестный мат, идентифицированный по составным словам имеющимся в словарях, но отсутствующий как таковой, записывается в отдельный лог, сам совец
при этом может отвечать стандартной фразой, формирующейся из 2 списков "я тебя " + [',типа, ',', как бы, ', ', вроде,'] + [услышал, понял,] или я тобой + [] + [восхищён, удивлён]
если мат ему знаком, то совец может стандартной фразой см выше пожурить, из списков слова выбираются random.choice
Еще неплохо бы вести лог с пользователем, чтобы следить чтобы тот не повторялся.
Если пишут не по русски, может цитировать Криминальное чтиво - on Russian, mothe******ing! и вообще еще один список ответов ему придумать.
Еще придумать как бы добавлять к одним фразам мат из словаря односложного мата Dict1.
еще сделать сам бот отдельной программой, а мейн должен его обслуживать, чтобы боту можно было обновляться reload по команде "окстись", чтобы можно было вносить
 изменения без необходимости ребутить всю программу.
еще сделать команду обновления словаря бота в онлайн режиме, который он инициализирует при запуске, чтобы не надо было даже перезагружать всю птицу,
чтобы она сохраняла свои временные настройки общения в виде логов общения с пользователями (которые по хорошему надо очищать перед каждым запуском)
Сами словари птицы хранятся как отдельные файлы определенной конфигурации и подгружаются при инициализации/обновлении словаря


Когда совец получает от кого-то сообщение, он проверяет не общается ли он уже с этим id
Для этого в ходе работы создается список экземпляров класса пользователь [Obj1,Obj2,..], где хранится id, и вообще все данные общения с этим пользователем,
Сам совец проходится циклом for по списку общения, если там не находит пользователя, то заводит нового пользователя в список и начинает общение.
В процессе выбора ответа, совец в полубесконечном цикле обязательно проходит по файлу/списку общения с пользователем, чтобы убедиться, что он так уже не отвечал, и если
не отвечал, то выходит брейком и отвечает, а если отвечал, то заново пытается составить ответ. При большом объеме словарей, замыкания быть не должно, но можно вставить на всякий случай
счётчик для выхода (10-100 итераций).
Если пользователь передразнивает совца, то он вопрошает "Я не понял, кто из нас попугай, ты или я?" и еще несколько таких фраз с обязательным списком мусорных [типа, как бы]
Список пользователей не должен быть неограниченным, ограничить его 100 человек, а при добавлении 101, опрашивать список на манер obj.last_talking, где хранить дату последнего
общения и при общении более 10 минут назад, просто удалять этого пользователя и вставлять нового, а при невозможности просто извинятся стандартной фразой.
ну и добавить ок - хуёк :-). Смайлики ещё можно вставить в необязательные фразы.
Надо чтобы совец матерился не на конкретного индивида, пусть выцепляет слова "он", "она", "они" и уже на них строит фразу "Пиздец, они упоротые", "А он, а она? иди ты!"
Добавить совцу игру в города - хранить результаты в списке, чтобы быстро его опрашивать, если промахивается спрашивать надоело? реагировать на "надоело", и "да" для выхода, при выборе ответа города делать рандом из списка подходящих
добавить совцу игру быки и коровы.
Добавить совцу игру в поле чудес? на троих игроков в чате?

добавить реакцию анекдот с поиском по другим существительным в данном сообщении "анекдот про прапорщика", а потом по этому существительному ищет аналоги в базе
Добавить реакцию на "ещё" бот смотрит предыдущее сообщение пользователя и повторяет этот сценарий, если он там был, с рекурсией по ещё
'''
import logging
import os, random, time, re, pickle

import settings
import vk_api, vk_api.bot_longpoll
from vk_api.bot_longpoll import VkBotLongPoll
from peewee import *
import sorter, filler_tickets, game_towns
from parser_name_from_vk import NameParser
from game_towns import GameTowns
from sea_battle import SeaBattle
from bulls_and_cows import BullsCows
from scenarios import Scenarios
import my_logger
from my_logger import log
try:
    from settings import TOKEN, GROUP_ID
except ImportError:
    exit('Copy settings.py.default to settings.py and set TOKEN as str and GROUP_ID as number!')

#from for_work_to_users import User
log.setLevel(logging.INFO)

class UserData:

    def __init__(self, id: int):

        self.id = id
        self.log = ''  # Строка, где хранится лог общения [time,obj,txt],[time,obj,txt]
        self.scenario = None  # переменная где хранится экземпляр сценария
        self.context = {}
        self.state = None


db = SqliteDatabase('user.db')

class UserDb(Model):
    id = IntegerField()
    name = CharField()
    log = TextField()  # Список, где хранится лог общения [[time,obj,txt],[time,obj,txt]] Непустой, чтобы не было ошибки итеракции по нему при опросе
    rage = IntegerField()  # переменная отношения бота к юзеру, изначально бот спокоен.
    filename = CharField() # имя файла сохраненной игры

    class Meta:
        database = db

db.create_tables([UserDb])
db.close()

def connection(func):
    db.connect()
    def wrapper(*args,**kwargs):
        return func(*args,**kwargs)
    db.close()
    return wrapper

class Bot:

    def __init__(self, group_id: int, token: str):
        self.dict = {}
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoller = VkBotLongPoll(self.vk, self.group_id, wait=25)
        self.api = self.vk.get_api()
        self.creator_dict = sorter.Sorter()   # Создание словаря для Бота в модуле sorter
        self.creator_dict.run()               # создает файлы для создания плохого словаря
        self.create_dict_bad_words()          # создает внутренний словарь бота
        self.upload = vk_api.VkUpload(vk=self.vk)
        self.names_scenarios = {GameTowns: ['города'], SeaBattle: ['морской', 'бой'], BullsCows: ['быки', 'коровы']}  # словарь классов игр и ключевых слов
        self.users = {1:'2'}  # словарь, где по id юзера хранится его экземпляр UserData
        self.db_users = {1: '2'}  # словарь, где по id юзера хранится его экземпляр UserDb

    def create_dict_bad_words(self):
        '''Делает словарь плохих слов из словарных файлов в dict_bad_words'''
        list_dict_files = sorter.Sorter().create_list_files(catalog='dict_bad_words',filter='dict_')  # возвращает список файлов в директории
        for dictionary in list_dict_files:
            with open(dictionary,'r',encoding='utf-8') as file:
                directory, name = dictionary.split('\\')
                name = name[5:-4]  #создаем имя словаря для последующей идентификации
                self.dict[name] = {}  # создаем словарь в словаре
                for line in file:
                    part1, part2 = line.rstrip().split('/')
                    self.dict[name][part1] = part2  # словарь {мат: запиканый мат}
        return

    def create_dict_good_words(self):
        '''Делает "словарь", точнее списки из словарных файлов в dict_good_words'''
        #TODO
        pass

    @connection
    def check_bad_words(self, event):
        '''Проверяет плохие слова по своему словарю'''
        words = event.message['text'].lower().split(' ')
        for word in words:
            for dictionary in self.dict.values():
                if word in dictionary.keys():
                    self.db_users[event.message['from_id']].rage += 10  # бот увеличивает злобу с каждым матом
                    self.db_users[event.message['from_id']].save()
                    return random.choice(['Ай, яй, яй!',"Нехорошо, молодой человек!",
                                        "А ещё боремся за почётное звание чата высокой культуры!",
                                        "Я в тебя полиция вызову!",
                                        "Стыдно, стыдно должно быть!",
                                        "Как тебе не стыдно!",
                                        "Будешь так делать, мама обидится",
                                        "Товарищ солдат, что Вы материтесь, как дитё малое!",
                                        "Боже мой, под каким забором Вас воспитывали?",
                                        "Да ты я вижу не уймешься!"])
    @connection
    def create_user(self, event):
        '''Создает пользователя для общения с ним, ключ int id пользователя'''

        user_id = event.message['from_id']  # хранение данных в виде экземпляра класса
        user = UserData(id=user_id)
        self.users[user_id] = user

        try:                    # ищем такого пользователя
            userdb = UserDb.select().where(UserDb.id == user_id).get()
            user.log = userdb.log
        except Exception:       # или создаем новую запись в БД
            url = 'https://vk.com/id' + str(user_id)  # хранение данных в виде базы данных
            new_user = NameParser(url)
            assumed_name = new_user.parse_name_user()
            userdb = UserDb.create(id=user_id, name=assumed_name, log='', rage=0, filename='')
            userdb.save()
        user.name = userdb.name
        self.db_users[user_id] = userdb  # сохраняем и этот экземпляр в БД. Пока идёт дубляж
        return

    @connection
    def log_and_send_user(self, event, answer: str):
        '''Логирует диалог с пользователем и посылает ответ'''

        time_now = time.gmtime(time.time() - time.timezone)
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time_now)
        user_id = event.message['from_id']
        self.db_users[user_id].log += 'user' + '\t' + date_time + '\t' + event.message['text'] + '\n'
        self.db_users[user_id].log += 'bot' + '\t' + date_time + '\t' + answer + '\n'
        self.db_users[user_id].save()
        self.users[user_id].log = self.db_users[user_id].log
        # self.users[user_id].log.append([date_time, 'user', event.message['text']])  # все сообщения хранятся в логе класса
        # self.users[user_id].log.append([date_time, 'bot', answer])  # в виде [data.'user',txt],[data,'bot',answer]...
        log.debug(self.users[user_id].log)

        self.api.messages.send(peer_id=event.message['peer_id'], random_id=event.message['random_id'], message=answer)
        return

    def check_list_of_users (self):
        '''Проверяет список пользователей на вопрос, нельзя ли удалить из него кого-то для добавления нового'''
        #TODO пока не требуется
        pass

    def run(self):
        for event in self.longpoller.listen():
            try:
                self.turning_event(event)
            except Exception as exc:
                log.exception(f'Ошибка {exc} в функции обработки события {event}')
                print(f'Ошибка в функции обработки события {exc}')

    def turning_event(self, event):
        '''
        event = object VkBotMessageEvent class

        VkBotEventType.GROUP_JOIN ещё не реализовано!
        VkBotEventType.MESSAGE_ALLOW ещё не реализовано!
        2022-01-05 18:42:01,713 - INFO - VkBotEventType.WALL_POST_NEW ещё не реализовано!
        Что-то пошло не так [901] Can't send messages for users without permission
        event.from_user = True - сообщение от юзера   и event.chat_id = None
        event.from_chat = True - сообщение из чата болталки  event.chat_id = 1
        event.group_id = 207692611 при этом одинаковый
        '''
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_REPLY:  #TODO проверить обработку когда юзер просто отвечает боту
            return
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_TYPING_STATE:
            return
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_EDIT:
            return

        if event.message:  # Для нетекстовых событий это обычно None, костыль от ошибки извлечения из None
            if event.message['from_id'] not in self.users.keys():  # проверка есть ли такой пользователь в списке общающихся
                self.create_user(event)    #если нет, создаем пользователя, а далее как обычно
                                           # на этом этапе у нас обязательно есть уже такой пользователь.

        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            if answer := self.treatment_new_message(event):  # False - возвращается, когда бот внутри уже сам всё сделал. В основном касается команд.
                self.log_and_send_user(event=event, answer=answer)  # если это была не команда, логируем общение
        else:
            log.info(f'{event.type} ещё не реализовано!')

    def treatment_new_message(self, event):
        '''Формирование ответа на новое входящее сообщение'''
        # 1. Проверка не в сценарии ли игрок(начало сценария смотри в _reply_on_template)
        user_id = event.message['from_id']
        user = self.users[user_id]  # Извлекаем экземпляр пользователя в UserState
        userdb = self.db_users[user_id]

        if user.scenario: # Значит игрок в каком-то сценарии
            answer = self.continue_scenario(event)
            return answer

        # 2. Проверка на мат
        answer = self.check_bad_words(event)
        if answer != None:  # То есть юзер ругается
            if userdb.rage > 99:  # Если бот разозлился, начинает материться в ответ
                answer = self._reply_bad_phrase(event.message)
            return answer  # Если бот еще не злой, отвечаем, что прислала функция

        # 3. Проверка не команда ли боту
        if any([_ in event.message['text'].lower() for _ in ['птиц','птичк','птенчик','канарейк']]):  # Команды боту!
            self._command(event)
            return False

        # 4. иначе обрабатываем сообщение по шаблону TODO сделать более интересный вариант вместо дефолтного ответа
        answer = self._reply_on_template(event.message)  # обычный ответ бота, основанный на шаблонах
        return answer

    @connection
    def _command(self, event):
        '''Функция управления ботом'''

        user_id = event.message['from_id']
        user = self.users[user_id]  # Извлекаем экземпляр пользователя в UserData
        userdb = self.db_users[user_id]  # Извлекаем экземпляр пользователя в UserDb
        text = event.message['text'].lower()
        if user_id != settings.ID_ADMIN:
            answer = random.choice(['Ты права сначала получи, а потом учи!', 'Да счас, разбежался!', 'Откуда вы такие наглые лезете!'])
            self.log_and_send_user(event=event, answer=answer)
            return
        if any([_ in text for _ in ['разозлись','злюка','злобный','бяка']]):
            userdb.rage = 100
            userdb.save()
            self.explosion_from_rage(event)
            return
        elif any([_ in text for _ in ['уходи','вали','канай','сдрисни','уйди', 'выйди']]):
            answer = random.choice(['Ну и ладно!', 'Пока!', 'Не очень то и хотелось!', 'Чава, какава!', 'Адьос!', 'Ауфвидерзеен!'])
            self.log_and_send_user(event=event, answer=answer)
            exit()
        elif any([_ in text for _ in ['успакойся','успокойся','успагойся','стихни']]):
            answer = random.choice(['Сэр, есть, сэр!', 'С удовольствием!', 'Слушаюсь и повинуюсь!', 'Милорд!', 'Яволь, майн херр!'])
            userdb.rage = 100
            userdb.save()
        elif any([_ in text for _ in ['добавь','дополни','пополни']]):  #добавить в словарь плохих слов
            answer = random.choice(['Нипонял!', 'Чо?', 'Сам добавляй!', 'Нихть!'])
            with open('for_sorting.txt','a', encoding='utf-8') as file:
                text = text.split(' ') #проверка на повтор не нужна, так как check_bad_word идет раньше !!
                bad_word = ''
                for word in text:
                    if any([_ in text for _ in ['птиц','птичк','птенчик','канарейк']]):
                        continue
                    if any([_ in text for _ in ['добавь','дополни','пополни']]):
                        continue
                    bad_word = word  # из трёх слов во фразе одно имя бота, второе команда, третье и пр слово плохое
                if bad_word:  # Если вдруг бот не смог найти плохое слово
                    part_of_speech = self.creator_dict.find_part_of_speech(bad_word)  #выдает строку 'Noun'...
                    self.dict[part_of_speech][bad_word] = '*ля'  #запихиваем в словарь с временным заменителем, чтобы
                                                                #нельзя было запихнуть одно слово дважды, ведь
                    bad_word = '\n' + bad_word                  #словари плохих слов проверяются до !!!
                    file.write(bad_word)
                    answer = random.choice(['Сэр, есть, сэр!', 'С удовольствием!', 'Слушаюсь и повинуюсь!', 'Милорд!',
                                            'Яволь, майн херр!'])
        else:
            answer='Нихть ферштеен!'
        self.log_and_send_user(event=event, answer=answer)
        return

    def _reply_on_template(self, message):
        '''Ответ на основе шаблонов'''
        text = message['text'].lower()
        for intent in settings.INTENTS:
            if any(token in text for token in intent['tokens']):
                if intent['scenario'] == None:
                    answer = random.choice(intent['answer'])
                    break
                else:   # запуск сценария
                    answer = self.start_scenario(message, intent['scenario'])
                    break

        else:  # значит ничего не совпало
            answer = random.choice(settings.DEFAULT_ANSWERS)
        return answer

    def _reply_bad_phrase(self, message):
        '''Бот ругается, когда его разозлили. Ответ, построенный в основном на части речи собеседника.
        Здесь мат можно не проверять, потому что он проверяется раньше'''
        words = message['text'].lower().split(' ')
        reply = ''
        for word in words:
            part_of_speech = self.creator_dict.find_part_of_speech(word)
            try:
                temp_dict = self.dict[part_of_speech]
            except KeyError:
                temp_dict = self.dict['None']
            if list(temp_dict.values()) == []:
                temp_dict = {'1':'э','2':'эээ'}
            random_word_the_same_part_of_speech = random.choice(list(temp_dict.values()))
            reply = reply + ' ' + random_word_the_same_part_of_speech
        return reply

    def explosion_from_rage(self, event):
        '''Бот в страшной ярости посылает юзеру билет, теоретически должен еще что-нибудь сделать
        типа поставить флаг и больше с юзером не общаться или занести его в черный список'''
        answer = ['Нах по-немецки обозначает направление, по-русски тоже, только более конкретно']
        user_id = event.message['from_id']
        userdb = self.db_users[user_id]
        #answer = 'Думаешь я тебя не узнаю, ' + assumed_name
        #self.to_vk.messages.send(peer_id=message['peer_id'], random_id=message['random_id'], attachment=photo100172_166443618)
        ticket = filler_tickets.Filler_tickets(name=userdb.name)
        ticket.fill()
        photo = self.upload.photo_messages('images/ticket_for_user.png')
        owner_id = photo[0]['owner_id']
        photo_id = photo[0]['id']
        access_key = photo[0]['access_key']
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        self.api.messages.send(peer_id=event.message['peer_id'], random_id=event.message['random_id'], attachment=attachment)

    def start_scenario(self, message, scenario: str):
        '''Запуск любой игры или сценария. Образует экземпляр соответствующего класса и пихает его в словарь играющих.
        Игра или сценарий:
            1. Должна быть сделана на классе.
            2. В классе должна иметь функцию run, которая принимает текстовую строку и отдает текстовую строку ответа.
            3. Должна иметь атрибут stage для сверки состояния игры.
            4. конец игры должен характеризоваться атрибутом stage = 'end the game'.
            5. Сохранение игры осуществляется посредством передачи в ответе ключевых слов в любом месте "Сохраняю игру".
            6. Сохранение игры осуществляется за счёт сохранения экземпляра, загрузка обратна.
            7. Сохраняемый экземпляр должен иметь атрибут message_after_load: str, который будет выдан юзеру после загрузки.
        '''

        user_id = message['from_id']
        text = message['text'].lower()
        words = text.split(' ')
        user = self.users[user_id]
                                     # теперь надо определить в какую игру
        if scenario == 'GAMES':
            founded_class = None
            for klass, names in self.names_scenarios.items():
                if any([_ in text for _ in names]):
                    founded_class = klass
            if not founded_class:
                return 'Я не знаю такой игры'

            if answer := self.load_games(founded_class, user_id):   # Если есть сохраненная игра, мы ее загружаем
                return answer                                       # и выдаем сохраненное сообщение после загрузки
            scenario_instance = founded_class(user)                  # иначе создаем экземпляр и начинаем игру
        else:                                                   # это не игра
            scenario_instance = Scenarios(user, scenario)      # создаем экземпляр текстовых сценариев

        user.scenario = scenario_instance
        answer = scenario_instance.run(' ')  # запускаем пустышку, чтобы получить стартовое сообщение сценария
        return answer

    def load_games(self, klass, user_id: int):
        '''Проверяет наличие файла, если нет возвращает False, если есть загружает его в массив игр игроков'''
        filename = 'saved_games/Saved_' + klass.__qualname__ + str(user_id) + '.svg'  # Вставляем имя класса и id игрока
        if not os.path.exists(filename):
            return False
        with open(filename, 'rb') as file:
            user_instance = pickle.load(file)
        self.users[user_id].scenario = user_instance  # заносим экземпляр в экземпляр пользователя
        answer = user_instance.message_after_load
        return answer

    def save_games(self, user_id: int, user_instance):
        '''Сохраняет экземпляр игры в определенной папке с названием класса и id пользователя'''
        filename = 'saved_games/Saved_' + user_instance.__class__.__qualname__ + str(user_id) + '.svg'
        with open(filename, 'wb') as file:
            pickle.dump(user_instance, file)
        self.users[user_id].scenario = None # стираем из экземпляра пользователя

    def continue_scenario(self, event):
        '''Обработка любой игры. Работает с экземпляром соответствующего класса, извлекаемый из соотв. словаря по id
        Игра:
            1. Должна быть сделана на классе.
            2. В классе должна иметь функцию run, которая принимает текстовую строку и отдает текстовую строку ответа.
            3. Должна иметь атрибут stage для сверки состояния игры.
            4. конец игры должен характеризоваться атрибутом stage = 'end the game'.
            5. Сохранение игры осуществляется посредством передачи в ответе ключевых слов в любом месте "Сохраняю игру".
            6. Сохранение игры осуществляется за счёт сохранения экземпляра, загрузка обратна.
            7. Сохраняемый экземпляр должен иметь атрибут message_after_load: str, который будет выдан юзеру после загрузки.
        '''

        name_of_user = ''                           # Если общение в личке, то обращение по имени к игроку не требуется
        user_id = event.message['from_id']
        users_turn = event.message['text']
        user = self.users[user_id]                           # извлекает экземпляр пользователя из словаря
        scenario_instance = user.scenario                    # извлекляет экземпляр сценария из экземпляра пользователя
        answer = scenario_instance.run(users_turn)           # посылает ответ игрока в экземпляр и получает ответ

        if event.message['peer_id'] != event.message['from_id']:  # значит счас мы в чате, а значит надо добавить имя
            name_of_user = user.name + ': '
        if scenario_instance.stage == 'end the game':  # выход из игры
            filename = 'saved_games/Saved_' + scenario_instance.__class__.__qualname__ + str(user_id) + '.svg'  # Вставляем имя класса и id игрока
            if os.path.exists(filename):  # значит такая игра была сохранена, теперь её надо удалить
                os.remove(filename)
            user.scenario = None
        elif 'Сохраняю игру' in answer:  # выход из игры с сохранением
            self.save_games(user_id,scenario_instance)
        return name_of_user + answer

if __name__ == '__main__':
    bot = Bot(group_id=GROUP_ID, token=TOKEN)
    bot.run()
