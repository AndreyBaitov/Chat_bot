import pymorphy2, os

class Sorter:
    '''Class for create dictionary file for Bot. Need some txt files with bad_chars
    Example
    x = Sorter()
    x.run()
    search dict_XXXX.txt in dir dict_...'''

    def __init__(self, filename='for_sorting.txt'):
        self.filename = filename
        self.morph = pymorphy2.MorphAnalyzer()  # создает 1 экземпляр на всю программу 15Мб
        self.dict_file_bad_chars =     {2:'dict_bad_words/list_of_2_bad_chars.txt',
                                        3:'dict_bad_words/list_of_3_bad_chars.txt',
                                        4:'dict_bad_words/list_of_4_bad_chars.txt',
                                        5:'dict_bad_words/list_of_5_bad_chars.txt'}
        self.create_list_of_bad_chars()  #Создает списки плохих буквосочетаний из файлов
        self.files_bad_part_of_speech = self.create_list_files(catalog='dict_bad_words', filter='dict_')  # создает список файлов словарей плохих слов
        self.files_good_part_of_speech = self.create_list_files(catalog='dict_good_words',filter='dict_')  # создает список файлов словарей хороших слов
        self.files_books = self.create_list_files(catalog='books')  # создает список файлов книг
        self.create_dicts_good_words()  #Создает словари-списки хороших слов, сортированные по типу

    def create_list_of_bad_chars(self):
        '''Создает списки плохих буквосочетаний из файлов'''
        self.list_2_bad = []
        self.list_3_bad = []
        self.list_4_bad = []
        self.list_5_bad = []
        dict_list_bad_chars = {2: self.list_2_bad, 3: self.list_3_bad, 4: self.list_4_bad, 5: self.list_5_bad}
        for number, list_char in dict_list_bad_chars.items():
            file_dict = self.dict_file_bad_chars[number]
            with open(file_dict, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.rstrip()
                    list_char.append(line)

    def create_list_files(self, catalog, filter=''):
        '''Создает и возвращает список путей к файлам словарей содержащих в себе filter в каталоге catalog'''
        path = os.getcwd()
        path = os.path.join(path, catalog)
        list_files = list(os.walk(path))[0][2]
        list_dict_files = []
        for filename in list_files:
            if filter in filename:
                path = os.path.join(catalog, filename)
                list_dict_files.append(path)  # создаем список словарей ['dict_ADJF.txt', 'dict_ADJS.txt', ...]
        return list_dict_files

    def sort_one_bad_word(self, line):
        '''Определяет часть речи, заменяет плохие буквы, записывает'''
        part_of_speech = self.find_part_of_speech(line)   #['NOUN', 'INFN', 'ADJF', 'INTJ', 'VERB', 'ADVB', 'ADJS', None, 'GRND']
        if part_of_speech == None:
            part_of_speech = 'None'
        filename = 'dict_bad_words/dict_' + part_of_speech + '.txt'
        self.replace_bad_str(line, file_dict=filename)
        return

    def sort_expression(self, line):
        '''сортирует выражения по количеству слов, затем проверяет каждое слово в выражении на bad_str'''
        pass

    def replace_bad_str(self, line, file_dict='not_sorted_by_type.txt'):
        '''заменяет нехорошие буквосочетания на ***, если не знает как, спрашивает пользователя'''
        line_initial = line
        if line == 'бля' or line == 'хер' or line == 'хуй':  # обработка самых простых матов
            line = line[:1] + '**'
        for char in self.list_5_bad:                         # проходим по спискам плохих буквосочетаний и заменяем
            line = line.replace(char, '*****', 10)
        for char in self.list_4_bad:
            line = line.replace(char, '****', 10)
        for char in self.list_3_bad:
            line = line.replace(char, '***', 10)
        for char in self.list_2_bad:
            line = line.replace(char, '**', 10)
        while '**' not in line:                                     # если ничего не заменилось
            line = line[0] + '*' * (len(line)-2) +line[-1]  #оставляем первую, последнюю, а поправится на рефайне
        save = line_initial + '/' + line + '\n'
        with open(file_dict, 'a', encoding='utf-8') as file:
            file.write(save)
        return

    def add_bad_chars(self, char):
        '''По внутренним словарям определяет куда отправить буквосочетание и отправляет'''
        dict = self.dict_list_bad_chars[len(char)]
        dict.append(char)
        filename = self.dict_file_bad_chars[len(char)]
        with open(filename, 'a', encoding='utf-8') as file:
            save = char + '\n'
            file.write(save)
        return

    def find_part_of_speech(self, line):
        '''Выдает 1 из
        NOUN 	имя существительное 	хомяк
        ADJF 	имя прилагательное (полное) 	хороший
        ADJS 	имя прилагательное (краткое) 	хорош
        COMP 	компаратив 	лучше, получше, выше
        VERB 	глагол (личная форма) 	говорю, говорит, говорил
        INFN 	глагол (инфинитив) 	говорить, сказать
        PRTF 	причастие (полное) 	прочитавший, прочитанная
        PRTS 	причастие (краткое) 	прочитана
        GRND 	деепричастие 	прочитав, рассказывая
        NUMR 	числительное 	три, пятьдесят
        ADVB 	наречие 	круто
        NPRO 	местоимение-существительное 	он
        PRED 	предикатив 	некогда
        PREP 	предлог 	в
        CONJ 	союз 	и
        PRCL 	частица 	бы, же, лишь
        INTJ 	междометие 	ой'''
        word = self.morph.parse(line)[0]  # word это эземпляр
        part_of_speech = word.tag.POS     # tag это эземпляр
        return part_of_speech

    def clear(self):
        '''before create this func deleted all files of part of speech'''
        list_of_type_speech = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ']
        for name in list_of_type_speech:
            filename = 'dict_bad_words/dict_' + name + '.txt'
            with open(filename,'w',encoding='utf-8'):
                pass
            filename = 'dict_good_words/dict_' + name + '.txt'
            with open(filename, 'w', encoding='utf-8'):
                pass
        return

    def refine(self):
        '''Улучшает слишком замыленные знаками ***** слова'''
        for file in self.files_bad_part_of_speech:
            temp_list = []
            with open(file,'r',encoding='utf-8') as current_file:  # сначала читаем весь файл в список
                for line in current_file:
                    line = line.rstrip()
                    temp_list.append(line)
            clear = open(file,'w',encoding='utf-8')  # стираем содержимое файла
            for part in temp_list:
                part1, part2 = part.split('/')
                if part2[0] == '*':
                    part2 = part1[0] + part2[1:]
                if part2[-1] == '*':
                    part2 = part2[:-1] + part1[-1]
                place = 0
                if '***' in part2:                      # работа с в*********ся
                    for i in range(len(part2)):
                        if part2[i] == '*':
                            place = i
                            part2 = part2[:i + 1] + part1[i + 1] + part2[i+2:]
                            break
                if '***' in part2[place+2:]:
                    for i in range(place+2,len(part2)):
                        if part2[i] == '*':
                            place = i
                            part2 = part2[:i + 1] + part1[i + 1] + part2[i+2:]
                            break
                if '***' in part2[place+2:]:
                    for i in range(place+2,len(part2)):
                        if part2[i] == '*':
                            place = i
                            part2 = part2[:i + 1] + part1[i + 1] + part2[i+2:]
                            break
                save = part1 + '/' + part2 + '\n'
                with open(file, 'a', encoding='utf-8') as current_file:
                    current_file.write(save)
        return

    def sort_one_good_word(self, word):
        '''Определяет часть речи, записывает в какой нужно список-множество'''
        # part_of_speech = self.find_part_of_speech(line)   #['NOUN', 'INFN', 'ADJF', 'INTJ', 'VERB', 'ADVB', 'ADJS', None, 'GRND']
        # if part_of_speech == None:
        #     part_of_speech = 'None'
        # filename = 'dict_bad_words/dict_' + part_of_speech + '.txt'
        # self.replace_bad_str(line, file_dict=filename)
        # TODO
        return

    def create_dicts_bad_words(self):
        '''split file of dict and distribute work'''
        file = open(self.filename, 'r', encoding='utf8')  # пока только в 1 файле
        for line in file:
            line = line.rstrip().lower()
            number_of_words = len(line.split(' '))
            if number_of_words == 1:
                self.sort_one_bad_word(line)
            else:
                self.sort_expression(line)

    def create_dicts_good_words(self):
        '''Делает "словари файлы хороших слов в dict_good_words из книг'''
        for file in self.files_books:
            with open(file, 'r', encoding='utf-8') as current_file:
                for line in current_file:
                    words = self.spliting(line)
                    for word in words:
                        self.sort_one_good_word(word)
        self.refine_files_of_good_words()

    def spliting(self, line):
        # TODO
        return ['a','b']

    def refine_files_of_good_words(self):
        '''Последовательно просматривает списки словарей, превращает в множества и записывает обратно'''
        #TODO
        #self.files_good_part_of_speech
        pass

    def run(self):
        self.clear()  # очищает все словари, чтобы не было дублирования
        self.create_dicts_bad_words()  # создает словари плохих слов
        self.create_dicts_good_words()  # Создает словари-списки хороших слов, сортированные по типу
        self.refine()  # подправляет слова вида *** и **ый на х*й и п*ый, а также жев*** на жев**й




if __name__ == '__main__':
    work = Sorter()
    work.run()  # очищает словари, чтобы не было дублирования
    print('ЖОПИЗДАН')








