'''Парсер имени пользователя по id вКонтакте. Основная функция выдает строку с именем'''
import my_logger, bs4, re
from my_logger import log
from bs4 import BeautifulSoup

import requests, os

class NameParser:

    def __init__(self, url):
        self.url = url

    def parse_name_user(self):
        html_data = self.get_html(url=self.url)
        html_doc = BeautifulSoup(html_data, features='html.parser')
        list_assumed_name1 = html_doc.find_all('title')
        list_assumed_name2 = html_doc.find_all('h2', {'class': 'op_header'})
        assumed_name1 = self.checking(list_assumed_name1)
        assumed_name2 = self.checking(list_assumed_name2)
        assumed_name1 = re.findall(r'(\w+\s\w+) \| ВКонтакте', assumed_name1)
        assumed_name1 = assumed_name1[0]
        if assumed_name1 == assumed_name2 :  # если оба имени совпадают
            assumed_name = assumed_name1
        else:
            assumed_name = max([assumed_name1, assumed_name2], key=len)
        log.debug(f'Предполагаемое имя = {assumed_name}')
        return assumed_name

    def checking(self,list_names):
        try:
            assumed_name = list_names[0].text
        except IndexError:
            assumed_name = ''
        return assumed_name

    # удаленная функция поиска в этом окружении, не смог понять как в bs4 это сделать
    # def search_on_meta_name(self, line):
    #     if '<meta name="description" content="' in line:
    #         line = line.replace('<meta name="description" content="', '')
    #         for char in line:
    #             if char == '.' or char == ',':
    #                 break
    #             self.assumed_name1 = self.assumed_name1 + char
    #     for char in self.assumed_name1:
    #         if char == ' ':
    #             self.assumed_name1 = self.assumed_name1[1:]
    #         else:
    #             break
    #     return

    def get_html(self, url):
        try:
            res = requests.get(url)
        except Exception:
            log.exception('Не смог загрузить данные пользователя по сети')
            return ''
        return res.text

if __name__ == '__main__':
    go = NameParser('https://vk.com/id395305264')  #395305264 - мой
    result = go.parse_name_user()
    print(result)
    go = NameParser('https://vk.com/id73877135')  #73877135 - сложный
    result = go.parse_name_user()
    print(result)