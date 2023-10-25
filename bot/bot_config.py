from bot.keyboards.inlinekeyboards import (inline_keyboard_title_notebooks,
                                           inline_keyboard_title_telephones,
                                           inline_keyboard_title_tables)

from decouple import config

from telebot import TeleBot

bot = TeleBot(config('BOT_TOKEN'))

bot_sub_menu = ['Ноутбуки', 'Компьютеры', 'Мониторы', 'Телефоны', 'Планшеты', 'Процессоры', 'Оперативная память',
                'Материнские платы', 'Кулеры', 'Корпуса', 'Жесткие диски', 'Видеокарты', 'Блоки питания',
                'SSD', 'Фотопринтеры', 'Сканеры', 'Принтеры', 'МФУ']


class UserData:
    def __init__(self):
        self.deleted = False
        self.title = None
        self.min_price = 0
        self.max_price = 0
        self.city = None
        self.msg_quantity = 0
        self.category = None
        self.user_registered = False

    def reset_data(self):
        self.deleted = False
        self.title = None
        self.min_price = 0
        self.max_price = 0
        self.city = None
        self.msg_quantity = 0


user_data = UserData()

keyboards_cats = {
    1: inline_keyboard_title_notebooks(),
    2: None,
    3: None,
    4: None,
    5: inline_keyboard_title_telephones(),
    6: inline_keyboard_title_tables(),
    7: None,
    8: None,
    9: None,
    10: None,
    11: None,
    12: None,

}