import re
import time
import settings
from email_sender import email_sender

name_pattern = re.compile(r'[А-Я,а-я]{2,20}')
email_pattern = re.compile(r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$')

def handler_name(name: str, context: dict):
    '''Получает на вход ФИО, проверяет, если всё нормально=True, плохо False'''
    parts = name.split(' ')
    if len(parts) != 3:
        return False
    for part in parts:
        if not re.match(name_pattern,part):
            return False
    context['name'] = name
    return True

def handler_email(email: str, context: dict):
    '''Получает на вход емейл, проверяет, если всё нормально=True, плохо False'''
    if not re.match(email_pattern, email):
        return False
    context['email'] = email
    return True

def handler_agree_regulations(message: str, context: dict):
    '''Получает на вход да или нет, если да, логирует заявку -> True, если нет, возвращает False'''

    message = message.lower()
    if any([_ in message for _ in ['да','lf','ага','fuf','yes']]):
        time_now = time.gmtime(time.time() - time.timezone)
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time_now)
        record = f'Камрад {context["name"]} с электронной почтой {context["email"]} подал заявку на вступление в клуб {date_time}.\n'
        with open('log/claims_for_club.txt','a', encoding='utf-8') as file:
            file.write(record)
        email_sender(message=record, subject='Заявка на вступление в клуб')
        return True
    return False


if __name__ == '__main__':
    print(handler_name('Андрей Анатольевич Баитов', {}))
    print(handler_name('Ац Анатольевич Баитов', {}))
    print(handler_email('fucking@mail.ru', {}))
    print(handler_email('fuckingmail.ru', {}))
    print(handler_agree_regulations('да', {'name':'Андрей Анатольевич Баитов','email':'fucking@mail.ru'}))
    print(handler_agree_regulations('нет', {'name': 'Андрей Анатольевич Баитов', 'email': 'fucking@mail.ru'}))
