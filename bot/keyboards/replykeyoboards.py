from telebot import types


def load_reply_keyboard_back_gen_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn)
    return markup

def load_reply_keyboard_with_gen_menu_and_next():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Далее')
    btn2 = types.KeyboardButton('🔙 Главное меню')
    markup.row(btn1, btn2)
    return markup

def load_reply_keyboard_gen_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Компьютерная техника 🖥')
    btn2 = types.KeyboardButton('Телефоны и планшеты 📱')
    # btn3 = types.KeyboardButton('Все для детей и мам 🛍')
    # btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
    # btn5 = types.KeyboardButton('Авто и транспорт 🚗')
    markup.add(btn1, btn2)
    return markup