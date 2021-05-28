#!/usr/bin/env python
# VERSON 3.5
from sys import flags
from typing import Text
import telebot
import requests
from bs4 import BeautifulSoup
import re
from telebot import types
import time
# Версия 1.0
#+ Написан парсер м/с
#+ Регулярными выражениями удалены лишнии символы
#+ Добавлены переносы строк
#+ Сделан вывод в бота 
# --------------------------
# Версия 2.0
#+ Добавлен парсер дат
#+ Сделать вывод дат в бота
#+ Добавить кнопку текущего обновления
#+ Рефакторинг кода
# --------------------------
# Версия 3.0
#+ Переписан алгоритм проверки чисел у значений ветра ( БЕТА )
#+ Допилить проверку на идеальные дни (НУЖЕН ГРАМОТНЫЙ ВЫВОД REGEXP)
#+ Сделан вывод по команде идеальных дней
#+ Написать функцию оповещения при идеальных погодных условиях
#+ Добавлена возможность отключения функции оповещения по команде /stop
# DEPLOY ON THE SERVER
# Исправлены баги: не верная проверка второго числа у ветра, проверялось значение от первого + не большой рефакторинг кода
# Версия 4.0
#- Будет добавлена возможность сохранять идеальные дни для статистики в отдельный файл
#- Просмотр в боте статистики идеальных дней по категориям

# Создаем класс DAY 
class Day(object):
    def __init__(self, data_time, two_hours, five_hours, condition):
        self.data_time = data_time
        self.two_hours = two_hours
        self.five_hours = five_hours
        self.condition = condition
    condition = False
    data_time = []
    two_hours = []
    five_hours = []

# ОСНОВНЫЕ ПЕРЕМЕННЫЕ
bot = telebot.TeleBot("1324955451:AAFwa1SJLtdS_txDryLjS4Ow9jcjNhqvviU", parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN
URLS = ['https://www.gismeteo.ru/weather-kopeysk-12862/', 'https://www.gismeteo.ru/weather-kopeysk-12862/tomorrow/', 'https://www.gismeteo.ru/weather-kopeysk-12862/3-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/4-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/5-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/6-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/7-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/8-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/9-day/', 'https://www.gismeteo.ru/weather-kopeysk-12862/10-day/']
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36', 
    'accept' :'*/*'}
TIMER = False

# парсим из исходного кода данные о ветре
def get_content(html):
            soup = BeautifulSoup(html, 'html.parser')    
            items = soup.find('div', class_='widget__row_wind-or-gust')
            weather = []
            for item in items:
                day = item.find('span', class_='unit_wind_m_s').get_text(strip=True)
                wther = re.findall(r'((\d\D\d)|\d)', day)
                weather.append(wther[0][0])
            return weather

# Получаем исходный код страницы с определенным набором юзер-агента по конкретному урлу и возвращаем это
def get_html(URL, params=None):
    r = requests.get(URL, headers=HEADERS, params=params)
    return r

# Парсер дат
def get_dates(URL):
            html = get_html(URL)
            if html.status_code == 200:
                soup = BeautifulSoup(html.text, 'html.parser')
                items = soup.find_all('div', class_='tab-content')
                days = []
                for item in items:
                    day = item.find('div', class_='date').get_text(strip=True)
                    days.append(day)
                for char in ',':
                    days[1] = days[1].replace(char, '')
                return days[1]
            else:
                return print('bad requestsssssss for get_dates')

# Парсим все ветра и оставляем только нужные за 2 и за 5 часов утра
def parse(URL):
            html = get_html(URL)
            if html.status_code == 200:
                days = get_content(html.text)
                while len(days) > 2:
                    del days[-1]
                return days
            else:
                return ('Erorr request to URL in varible "html"')


# создаем список идеальной погоды
def create_ideal_weather(wind):
    # разбиваем значение между тире "число-чисто" по переменным
    print('ALL: '+wind[0] + ' ' + wind[1])
    main_part_digit = 'None'
    one_part_digit = re.findall(r'\d-', wind[0])
    two_part_digit = re.findall(r'-\d+', wind[0])
    yes_or_no = False
    if not one_part_digit:
        main_part_digit = wind[0]
        # проверяем идеальные условия погоды
        if int(main_part_digit) < 4:
            yes_or_no = True
        else:
            yes_or_no = False
    else:
        one_part_digit = re.sub('\D', '', str(one_part_digit))
        two_part_digit = re.sub('\D', '', str(two_part_digit))
        print(str(one_part_digit[0])+str(two_part_digit[0]))
        # проверяем идеальные условия погоды
        if int(one_part_digit[0]) <= 2 & int(two_part_digit[0]) <=5:
            yes_or_no = True
        else: 
            yes_or_no = False 
    # делаем тоже самое только для 5 часов утра
    main_part_digit = 'None'
    one_part_digit = re.findall(r'\d-', wind[1])
    two_part_digit = re.findall(r'-\d+', wind[1])
    yes_or_no = False
    if not one_part_digit:
        main_part_digit = wind[0]
        # проверяем идеальные условия погоды
        if int(main_part_digit) < 4:
            yes_or_no = True
        else:
            yes_or_no = False
    else:
        one_part_digit = re.sub('\D', '', str(one_part_digit))
        two_part_digit = re.sub('\D', '', str(two_part_digit))
        print(str(one_part_digit[0])+str(two_part_digit[0]))
        # проверяем идеальные условия погоды
        if int(one_part_digit[0]) <= 2 & int(two_part_digit[0]) <= 5:
            yes_or_no = True
        else: 
            yes_or_no = False 
    # тычкуем в список идеальных дней
    if yes_or_no == True:
        print('okay, add this day')
        return True
    else:
        print('okay, miss this day')
        return False
        
# Создаем список погоды на 10 дней
def create_lists_weather():
    DAYS = []
    ideal = []
    for index, URL in enumerate(URLS):
        wind = parse(URL)
        if index == 0:
            DAYS.append(Day('Сегодня', wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 1:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 2:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 3:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 4:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 5:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 6:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 7:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 8:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))
        elif index == 9:
            DAYS.append(Day(get_dates(URL), wind[0], wind[1], create_ideal_weather(wind)))

    return DAYS

# Вывод погоды в бота
def show_weather(DAYS):
    list_weather = []
    for day in DAYS:
        list_weather.append(day.data_time)
        list_weather.append(day.two_hours + ' м/с')
        list_weather.append(day.five_hours + ' м/с')
        list_weather.append('')
    # Удаляем лишние символы в строковой переменной итоговой погоды
    result = str(list_weather)
    for char in '[\'':
        result = result.replace(char, '')
    for char in ',':
        result = result.replace(char, '\n')
    for char in ']':
        result = result.replace(char, '\n')
    return result
    
# Функция оповещения при идеальных условиях
def notice_ideal_days():   
        DAYS = create_lists_weather()
        list_weather = []
        for day in DAYS:
            if day.condition == True:
                list_weather.append(day.data_time)
                list_weather.append(day.two_hours + ' м/с')
                list_weather.append(day.five_hours + ' м/с')
                list_weather.append('')
        # Удаляем лишние символы в строковой переменной итоговой погоды
        result = str(list_weather)
        for char in '[\'':
            result = result.replace(char, '')
        for char in ',':
            result = result.replace(char, '\n')
        for char in ']':
            result = result.replace(char, '\n')
        return result
        
# Создаем клавиатуру и одну кнопку "обновить" 
markup = types.InlineKeyboardMarkup(row_width=1)
button_refresh = types.InlineKeyboardButton('Показать всю погоду', callback_data='refresh')
markup.add(button_refresh)

# Перехватываем команду старт и отправляем погоду и прикрепляем кнопку "Обновить"
@bot.message_handler(commands=['start'])
def send_weather(message):
    bot.send_message(message.chat.id, show_weather(create_lists_weather()), reply_markup=markup)

# Команда /stop меняет значение глобальной переменной TIMER - отключает функцию оповещения
@bot.message_handler(commands=['stop'])   
def change_TIMER(message):
    global TIMER 
    if TIMER:
        if TIMER == True: 
            TIMER = False
        else: 
            TIMER = True
    bot.send_message(message.chat.id,  'Вывод по таймингу отключен! Пошел нахуй - с новым годом!', reply_markup=markup)

# По команде /timer включается оповещение по времени о идеальной погоде раз в 30 секунд
@bot.message_handler(commands=['timer'])   
def send_notice(message):
    global TIMER
    if TIMER == False:
        TIMER = True
    else: 
        TIMER = False
    while TIMER == True:
        bot.send_message(message.chat.id,  notice_ideal_days(), reply_markup=markup)
        time.sleep(60*60*12)

# Перехватываем callback по нажатой кнопке и выполняем алгоритм: отправить текущую погоду и прикрепить кнопку "обновить"
@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.message:
        if call.data == 'refresh':            
            bot.send_message(call.message.chat.id, show_weather(create_lists_weather()), reply_markup=markup)

# Запускаем бота
bot.polling()