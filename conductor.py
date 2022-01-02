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
import sorter, filler_tickets, game_towns
from parser_name_from_vk import NameParser
from game_towns import GameTowns
import my_logger
from my_logger import log
try:
    from settings import TOKEN, GROUP_ID
except ImportError:
    exit('Copy settings.py.default to settings.py and set TOKEN as str and GROUP_ID as number!')

#from for_work_to_users import User

log.setLevel(logging.DEBUG)
#TODO где то в коде TypeError: 'NoneType' object is not subscriptable Возникает тогда, когда вы пытаетесь по индексу обратиться к None Объекту. когда что-то делается в личном чате, в общем проблемы нет

class Bot:
    def __init__(self, group_id, token):
        self.dict = {}
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.bot_longpoller = VkBotLongPoll(self.vk, self.group_id, wait=25)
        self.api = self.vk.get_api()
        self.creator_dict = sorter.Sorter()   # Создание словаря для Бота в модуле sorter
        self.creator_dict.run()               # создает файлы для создания плохого словаря
        self.create_dict_bad_words()          # создает внутренний словарь бота
        self.rage = {1:'2'}   #Словарь, где по id юзера хранится ярость бота
        self.upload = vk_api.VkUpload(vk=self.vk)
        self.array_users = {1:'2'}  #словарь, где по id: int юзера хранится лог {123456:[[time,obj,txt],[time,obj,txt]]} Непустой, чтобы не было ошибки итеракции по нему при опросе
        self.array_users_in_scenario = {1:'2'}  #словарь, где по id: int юзера хранится name: str сценария

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

    def check_bad_words(self, event):
        '''Проверяет плохие слова по своему словарю'''
        words = event.message['text'].lower().split(' ')
        for word in words:
            for dictionary in self.dict.values():
                if word in dictionary.keys():
                    self.rage[event.message['from_id']] += 10  # бот начинает закипать
                    return random.choice(['Ай, яй, яй!',"Нехорошо, молодой человек!",
                                        "А ещё боремся за почётное звание чата высокой культуры!",
                                        "Я в тебя полиция вызову!",
                                        "Стыдно, стыдно должно быть!",
                                        "Как тебе не стыдно!",
                                        "Будешь так делать, мама обидится",
                                        "Товарищ солдат, что Вы материтесь, как дитё малое!",
                                        "Боже мой, под каким забором Вас воспитывали?",
                                        "Да ты я вижу не уймешься!"])

    def create_user(self, event):
        '''Создает пользователя для общения с ним, ключ int id пользователя'''
        self.array_users[event.message['from_id']] = []  #{123456:[[time,obj,txt],[time,obj,txt]]} Именно число!
        self.rage[event.message['from_id']] = 0  # изначально бот спокоен
        self.array_users_in_scenario[event.message['from_id']] = None  #изначально никакого сценария у юзера нет
        return

    def log_and_send_user(self, event, answer):
        '''Логирует диалог с пользователем и посылает ответ'''
        time_now = time.gmtime(time.time() - time.timezone)
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time_now)
        self.array_users[event.message['from_id']].append([date_time, 'user', event.message['text']])  #{'id=123456':[[time,obj,txt],]}
        self.array_users[event.message['from_id']].append([date_time, 'bot', answer])
        log.debug(self.array_users[event.message['from_id']])
        self.api.messages.send(peer_id=event.message['peer_id'], random_id=event.message['random_id'], message=answer)
        return

    def check_list_of_users (self):
        '''Проверяет список пользователей на вопрос, нельзя ли удалить из него кого-то для добавления нового'''
        #TODO пока не требуется
        pass

    def run(self):
        for event in self.bot_longpoller.listen():
            try:
                self.on_event(event)
            except Exception as exc:
                log.exception(f'Что-то пошло не так {exc}')
                print(f'Что-то пошло не так {exc}')

    def on_event(self, event):
        '''
        event = object VkBotMessageEvent class

        VkBotEventType.GROUP_JOIN ещё не реализовано!
        VkBotEventType.MESSAGE_ALLOW ещё не реализовано!
        Что-то пошло не так [901] Can't send messages for users without permission
        event.from_user = True - сообщение от юзера   и event.chat_id = None
        event.from_chat = True - сообщение из чата болталки  event.chat_id = 1
        event.group_id = 207692611 при этом одинаковый
        '''
        log.debug(f"{event.message['from_id']},self.array_users.keys()= {self.array_users.keys()}")
        if event.message['from_id'] not in self.array_users.keys():  # проверка есть ли такой пользователь в списке общающихся
            self.create_user(event)    #если нет, создаем пользователя, а далее как обычно
                                       # на этом этапе у нас обязательно есть уже такой пользователь.

        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            answer = self.message_new(event)  # вызываем функцию обработки
            if answer:  # False - возвращается, когда бот внутри уже сам всё сделал. В основном касается команд.
                self.log_and_send_user(event=event, answer=answer)
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_TYPING_STATE:
            return
        elif event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_REPLY:  #TODO проверить обработку когда юзер просто отвечает боту
            return
        else:
            log.info(f'{event.type} ещё не реализовано!')

    def message_new(self, event):
        '''Формирование ответа на новое входящее сообщение'''
        # 1. Проверка не в сценарии ли игрок(начало сценария смотри в _reply_on_template)
        if self.array_users_in_scenario[event.message['from_id']] != None:  # Значит игрок в каком-то сценарии
            name = ''
            if self.array_users_in_scenario[event.message['from_id']].__class__ == GameTowns:   # игра в города
                town = event.message['text']
                game = self.array_users_in_scenario[event.message['from_id']]  #извлекает экземпляр из словаря
                answer = game.game(town)  # посылает город игрока в экземпляр и получает ответ
                log.debug(f'{event.message["peer_id"]},{event.message["from_id"]}')
                if event.message['peer_id'] != event.message['from_id']:  # значит счас мы в чате, а значит надо добавить имя
                    name = game.name + ': '
                if 'Горе мне' in answer or 'похоже я выиграл!' in answer:  #выход из игры
                    filename = 'saved_games/towns/Saved_' + str(event.message['from_id']) + '.svg'
                    if os.path.exists(filename):  # значит такая игра была сохранена, теперь её надо удалить
                        os.remove(filename)
                    self.array_users_in_scenario[event.message['from_id']] = None
                elif 'Сохраняю игру' in answer:  # выход из игры с сохранением
                    filename = 'saved_games/towns/Saved_' + str(event.message['from_id']) + '.svg'
                    user_instance = self.array_users_in_scenario[event.message['from_id']]
                    with open(filename, 'wb') as file:
                        pickle.dump(user_instance, file)
                    self.array_users_in_scenario[event.message['from_id']] = None  # стираем из памяти
            else:
                answer = 'Не знаю, во что играешь ты, но я такой игры не знаю'

            return name + answer

        # 2. Проверка на мат
        answer = self.check_bad_words(event)
        if answer != None:  # То есть юзер ругается
            if self.rage[event.message['from_id']] > 99:  # Если бот разозлился, начинает материться в ответ
                answer = self._reply_bad_phrase(event.message)
            return answer  # Если бот еще не злой, отвечаем, что прислала функция

        # 3. Проверка не команда ли боту
        if any([_ in event.message['text'].lower() for _ in ['птиц','птичк','птенчик','канарейк']]):  # Команды боту!
            self._command(event)
            return False

        # 4. иначе обрабатываем сообщение по шаблону TODO сделать более интересный вариант вместо дефолтного ответа
        answer = self._reply_on_template(event.message)  # обычный ответ бота, основанный на шаблонах
        return answer

    def _command(self, event):
        '''Функция управления ботом'''
        if event.message['from_id'] != settings.ID_ADMIN:
            answer = random.choice(['Ты права сначала получи, а потом учи!', 'Да счас, разбежался!', 'Откуда вы такие наглые лезете!'])
            self.log_and_send_user(event=event, answer=answer)
            return
        if any([_ in event.message['text'].lower() for _ in ['разозлись','злюка','злобный','бяка']]):
            self.rage[event.message['from_id']] = 100
            self.explosion_from_rage(event)
        elif any([_ in event.message['text'].lower() for _ in ['уходи','вали','канай','сдрисни']]):
            answer = random.choice(['Ну и ладно!', 'Пока!', 'Не очень то и хотелось!', 'Чава, какава!', 'Адьос!', 'Ауфвидерзеен!'])
            self.log_and_send_user(event=event, answer=answer)
            exit()
        elif any([_ in event.message['text'].lower() for _ in ['успакойся','успокойся','успагойся','стихни']]):
            answer = random.choice(['Сэр, есть, сэр!', 'С удовольствием!', 'Слушаюсь и повинуюсь!', 'Милорд!', 'Яволь, майн херр!'])
            self.rage[event.message['from_id']] = 0
            self.log_and_send_user(event=event, answer=answer)
        elif any([_ in event.message['text'].lower() for _ in ['добавь','дополни','пополни']]):  #добавить в словарь плохих слов
            answer = random.choice(['Нипонял!', 'Чо?', 'Сам добавляй!', 'Нихть!'])
            with open('for_sorting.txt','a', encoding='utf-8') as file:
                text = event.message['text'].lower() #проверка на повтор не нужна, так как check_bad_word идет раньше !!
                text = text.split(' ')
                bad_word = ''
                for word in text:
                    if any([_ in text for _ in ['птиц','птичк','птенчик','канарейк']]):
                        continue
                    if any([_ in event.message['text'].lower() for _ in ['добавь','дополни','пополни']]):
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
            self.log_and_send_user(event=event, answer=answer)
        else:
            self.log_and_send_user(event=event, answer='Нихть ферштеен!')
        return

    def _reply_on_template(self, message):
        '''Ответ на основе шаблонов'''
        text = message['text'].lower()
        for intent in settings.INTENTS:
            if any(token in text for token in intent['tokens']):
                if intent['scenario'] == None:
                    answer = random.choice(intent['answer'])
                    break
                else:                                          #run scenario
                    if intent['scenario'] == 'TOWNS':
                        answer = self.start_game_towns(message)           # начать игру в города
                    else:
                        answer = 'Таких игр пока нет'
                    return answer
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
        url = 'https://vk.com/id' + str(event.message['from_id'])
        user = NameParser(url)
        assumed_name = user.parse_name_user()
        #answer = 'Думаешь я тебя не узнаю, ' + assumed_name
        #self.to_vk.messages.send(peer_id=message['peer_id'], random_id=message['random_id'], attachment=photo100172_166443618)
        ticket = filler_tickets.Filler_tickets(name=assumed_name)
        ticket.fill()
        photo = self.upload.photo_messages('images/ticket_for_user.png')
        owner_id = photo[0]['owner_id']
        photo_id = photo[0]['id']
        access_key = photo[0]['access_key']
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
        self.api.messages.send(peer_id=event.message['peer_id'], random_id=event.message['random_id'], attachment=attachment)

    def start_game_towns(self, message):
        '''функция запуска игры в города. Образуем экземпляр соответствующего класса и пихаем его в массив играющих'''
        filename = 'saved_games/towns/Saved_' + str(message['from_id']) + '.svg'
        if os.path.exists(filename):  # значит такая игра была сохранена
            with open(filename, 'rb') as file:
                user_instance = pickle.load(file)
            self.array_users_in_scenario[message['from_id']] = user_instance
            last_town = user_instance.list_choosed_towns[-1]
            reply = f'Продолжаем! Последний названный город - {last_town}. Твой ход.'
            return reply
        self.array_users_in_scenario[message['from_id']] = GameTowns(message['from_id'])
        reply = 'Добро пожаловать в игру "Города", ты начинаешь!'
        return reply


if __name__ == '__main__':
    bot = Bot(group_id=GROUP_ID, token=TOKEN)
    bot.run()
