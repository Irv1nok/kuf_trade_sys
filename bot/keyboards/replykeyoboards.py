from telebot import types

from bot.bot_config import user_data


def reply_keyboard_back_gen_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn)
    return markup


def reply_keyboard_back_gen_menu_and_next():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Далее')
    btn2 = types.KeyboardButton('🔙 Главное меню')
    markup.row(btn1, btn2)
    return markup


def reply_keyboard_back_gen_menu_and_repeat():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Повторить ввод?')
    btn2 = types.KeyboardButton('🔙 Главное меню')
    markup.row(btn1, btn2)
    return markup

def reply_keyboard_back_gen_menu_and_yes_no_next():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Новые')
    btn2 = types.KeyboardButton('Б/У')
    btn3 = types.KeyboardButton('Далее')
    btn5 = types.KeyboardButton('🔙 Главное меню')
    markup.row(btn1, btn2)
    markup.row(btn3, btn5)
    return markup


def reply_keyboard_gen_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Компьютерная техника. 🖥')
    btn2 = types.KeyboardButton('Телефоны и планшеты. 📱')
    btn3 = types.KeyboardButton('Строительный инструмент. 🛠')
    # btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
    # btn5 = types.KeyboardButton('Авто и транспорт 🚗')
    markup.row(btn1, btn2)
    markup.row(btn3)
    return markup
