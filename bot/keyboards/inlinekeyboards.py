from telebot import types


def inline_keyboard_title_notebooks():
    markup_inline = types.InlineKeyboardMarkup()
    bk1 = types.InlineKeyboardButton(text='Acer', callback_data='title|Ноутбуки|Acer')
    bk2 = types.InlineKeyboardButton(text='Alienware', callback_data='title|Ноутбуки|Alienware')
    bk3 = types.InlineKeyboardButton(text='Apple', callback_data='title|Ноутбуки|Apple')
    bk4 = types.InlineKeyboardButton(text='ASUS', callback_data='title|Ноутбуки|ASUS')
    bk5 = types.InlineKeyboardButton(text='Dell', callback_data='title|Ноутбуки|Dell')
    bk6 = types.InlineKeyboardButton(text='Gigabyte', callback_data='title|Ноутбуки|Gigabyte')
    bk7 = types.InlineKeyboardButton(text='Honor', callback_data='title|Ноутбуки|Honor')
    bk8 = types.InlineKeyboardButton(text='HP', callback_data='title|Ноутбуки|HP')
    bk9 = types.InlineKeyboardButton(text='Huawei', callback_data='title|Ноутбуки|Huawei')
    bk10 = types.InlineKeyboardButton(text='Lenovo', callback_data='title|Ноутбуки|Lenovo')
    bk11 = types.InlineKeyboardButton(text='MSI', callback_data='title|Ноутбуки|MSI')
    bk12 = types.InlineKeyboardButton(text='Xiaomi', callback_data='title|Ноутбуки|Xiaomi')
    markup_inline.add(bk1, bk2, bk3, bk4, bk5, bk6, bk7, bk8, bk9, bk10, bk11, bk12)
    return markup_inline


def inline_keyboard_title_telephones():
    markup_inline = types.InlineKeyboardMarkup()
    bk1 = types.InlineKeyboardButton(text='ASUS', callback_data='title|Телефоны|ASUS')
    bk2 = types.InlineKeyboardButton(text='Apple', callback_data='title|Телефоны|Apple')
    bk3 = types.InlineKeyboardButton(text='HTC', callback_data='title|Телефоны|HTC')
    bk4 = types.InlineKeyboardButton(text='Honor', callback_data='title|Телефоны|Honor')
    bk5 = types.InlineKeyboardButton(text='Huawei', callback_data='title|Телефоны|Huawei')
    bk6 = types.InlineKeyboardButton(text='MEIZU', callback_data='title|Телефоны|MEIZU')
    bk7 = types.InlineKeyboardButton(text='OPPO', callback_data='title|Телефоны|OPPO')
    bk8 = types.InlineKeyboardButton(text='OnePlus', callback_data='title|Телефоны|OnePlus')
    bk9 = types.InlineKeyboardButton(text='Realme', callback_data='title|Телефоны|Realme')
    bk10 = types.InlineKeyboardButton(text='Samsung', callback_data='title|Телефоны|Samsung')
    bk11 = types.InlineKeyboardButton(text='Xiaomi', callback_data='title|Телефоны|Xiaomi')
    bk12 = types.InlineKeyboardButton(text='ZTE', callback_data='title|Телефоны|ZTE')
    markup_inline.add(bk1, bk2, bk3, bk4, bk5, bk6, bk7, bk8, bk9, bk10, bk11, bk12)
    return markup_inline


def inline_keyboard_title_tables():
    markup_inline = types.InlineKeyboardMarkup()
    bk1 = types.InlineKeyboardButton(text='ASUS', callback_data='title|Планшеты|ASUS')
    bk2 = types.InlineKeyboardButton(text='Apple', callback_data='title|Планшеты|Apple')
    bk3 = types.InlineKeyboardButton(text='BQ-Mobile', callback_data='title|Планшеты|BQ-Mobile')
    bk4 = types.InlineKeyboardButton(text='Honor', callback_data='title|Планшеты|Honor')
    bk5 = types.InlineKeyboardButton(text='Huawei', callback_data='title|Планшеты|Huawei')
    bk6 = types.InlineKeyboardButton(text='Lenovo', callback_data='title|Планшеты|Lenovo')
    bk7 = types.InlineKeyboardButton(text='Microsoft', callback_data='title|Планшеты|Microsoft')
    bk8 = types.InlineKeyboardButton(text='Samsung', callback_data='title|Планшеты|Samsung')
    bk9 = types.InlineKeyboardButton(text='Teclast', callback_data='title|Планшеты|Teclast')
    bk10 = types.InlineKeyboardButton(text='Xiaomi', callback_data='title|Планшеты|Xiaomi')

    markup_inline.add(bk1, bk2, bk3, bk4, bk5, bk6, bk7, bk8, bk9, bk10)
    return markup_inline


def inline_keyboard_city():
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.row_width = 2
    bk1 = types.InlineKeyboardButton(text='Минск', callback_data='city|Минск,')
    bk2 = types.InlineKeyboardButton(text='Минская обл.', callback_data='city|Минская')
    bk3 = types.InlineKeyboardButton(text='Брест', callback_data='city|Брест')
    bk4 = types.InlineKeyboardButton(text='Брестская обл.', callback_data='city|Брестская')
    bk5 = types.InlineKeyboardButton(text='Гродно', callback_data='city|Гродно')
    bk6 = types.InlineKeyboardButton(text='Гродненская обл.', callback_data='city|Гродненская')
    bk7 = types.InlineKeyboardButton(text='Могилев', callback_data='city|Могилев')
    bk8 = types.InlineKeyboardButton(text='Могилевская обл.', callback_data='city|Могилевская')
    bk9 = types.InlineKeyboardButton(text='Витебск', callback_data='city|Витебск')
    bk10 = types.InlineKeyboardButton(text='Витебская обл', callback_data='city|Витебская')
    markup_inline.add(bk1, bk2, bk3, bk4, bk5, bk6, bk7, bk8, bk9, bk10)
    return markup_inline


def inline_keyboard_delete_search_item(obj):
    markup_inline = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Удалить из поиска', callback_data=f'search|delete|{obj}')
    markup_inline.add(btn1)
    return markup_inline
