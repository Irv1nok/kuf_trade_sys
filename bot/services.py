import logging
from parser.models import Category, KufarItems
from time import sleep

from decouple import config

from telebot import TeleBot, types

logger = logging.getLogger(__name__)


def start_bot():
    category = None
    bot = TeleBot(config('BOT_TOKEN'))
    bot_sub_menu = ['Ноутбуки', 'Компьютеры', 'Мониторы', 'Телефоны', 'Планшеты', 'Процессоры', 'Оперативная память',
                    'Материнские платы', 'Кулеры', 'Корпуса', 'Жесткие диски', 'Видеокарты', 'Блоки питания',
                    'SSD', 'Фотопринтеры', 'Сканеры', 'Принтеры', 'МФУ']

    @bot.message_handler(commands=['start'])  # стартовая команда
    def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Компьютерная техника 🖥')
        btn2 = types.KeyboardButton('Телефоны и планшеты 📱')
        btn3 = types.KeyboardButton('Все для детей и мам 🛍')
        btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
        btn5 = types.KeyboardButton('Авто и транспорт 🚗')

        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id, "👋 Вас приветствует Kufar Bot", reply_markup=markup)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел')

    @bot.message_handler(commands=['fav'])
    def get_my_id(message):
        bot.send_message(message.from_user.id,
                         text=f'Избранное 🔄{message.from_user.id}',
                         parse_mode="Markdown")

    @bot.message_handler(commands=['help'])
    def show_help(message):
        bot.send_message(message.from_user.id,
                         text='Бот находится в стадии разработки,'
                              'в случае любых сложностей перезапустите бота.',
                         parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        print(call)
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        nonlocal category
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if message.text == 'Компьютерная техника 🖥':
            btn1 = types.KeyboardButton('Ноутбуки')
            btn2 = types.KeyboardButton('Компьютеры')
            btn3 = types.KeyboardButton('Мониторы')
            btn4 = types.KeyboardButton('Комплектующие')
            btn5 = types.KeyboardButton('Оргтехника')
            btn9 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn2, btn3, btn4, btn5, btn9)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Телефоны и планшеты 📱':
            btn1 = types.KeyboardButton('Телефоны')
            btn2 = types.KeyboardButton('Планшеты')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Комплектующие':
            btn1 = types.KeyboardButton('Процессоры')
            btn2 = types.KeyboardButton('Оперативная память')
            btn3 = types.KeyboardButton('Материнские платы')
            btn4 = types.KeyboardButton('Видеокарты')
            btn5 = types.KeyboardButton('Блоки питания')
            btn6 = types.KeyboardButton('SSD')
            btn7 = types.KeyboardButton('Кулеры')
            btn8 = types.KeyboardButton('Корпуса')
            btn9 = types.KeyboardButton('Жесткие диски')
            btn10 = types.KeyboardButton('🔙 Главное меню')
            markup.row(btn1, btn2, btn3, btn4)
            markup.row(btn5, btn6, btn7, btn8)
            markup.row(btn9, btn10)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Оргтехника':
            btn1 = types.KeyboardButton('МФУ')
            btn2 = types.KeyboardButton('Принтеры')
            btn3 = types.KeyboardButton('Сканеры')
            btn4 = types.KeyboardButton('Фотопринтеры')
            btn5 = types.KeyboardButton('🔙 Главное меню')
            markup.row(btn1, btn2, btn3, btn4)
            markup.row(btn5)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text in bot_sub_menu:
            category = get_category_from_bd(message)
            btn1 = types.KeyboardButton('5')
            btn2 = types.KeyboardButton('10')
            btn3 = types.KeyboardButton('15')
            btn4 = types.KeyboardButton('20')
            btn5 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn2, btn3, btn4, btn5)
            bot.send_message(message.from_user.id, 'Сколько объявлений показать?\nВыберите, или введите в чат *число:*',
                             reply_markup=markup,
                             parse_mode="Markdown")
            bot.register_next_step_handler(message, get_query_params)

        elif message.text == '🔙 Главное меню':
            category = None
            btn1 = types.KeyboardButton('Компьютерная техника 🖥')
            btn2 = types.KeyboardButton('Телефоны и планшеты 📱')
            btn3 = types.KeyboardButton('Все для детей и мам 🛍')
            btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
            btn5 = types.KeyboardButton('Авто и транспорт 🚗')
            markup.add(btn1, btn2, btn3, btn4, btn5)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    def get_query_params(message):
        if message.text == '🔙 Главное меню':
            return get_text_messages(message)
        try:
            msg_count = int(message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Нет')
            deleted = bot.reply_to(message, 'Показать проданные объявления? 💬', reply_markup=markup)
            bot.register_next_step_handler(deleted, get_query_data, msg_count)
        except ValueError:
            msg_count = bot.reply_to(message, '*Ошибка! Введите число. Повторите ввод:* 💬', parse_mode="Markdown")
            bot.register_next_step_handler(msg_count, get_query_params)

    def get_query_data(message, msg_count):
        del_obj = True if message.text == 'Да' else False

        query = KufarItems.objects.filter(cat_id=category).filter(deleted=del_obj).order_by(
            '-date' if not del_obj else "-time_create")
        qs_generator = init_qs_generator(query)
        query_data(message, qs_generator, msg_count)

    def init_qs_generator(query):
        for q in query:
            yield q

    def query_data(message, qs_generator, msg_count):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if message.text == '🔙 Главное меню':
            return get_text_messages(message)
        count = 0
        while count != msg_count:
            try:
                query = next(qs_generator)
                send_message(user_id=message.from_user.id, query=query)
                count += 1
            except Exception as ex:
                logger.error(f'Exception - {ex} in show_query_data')
                bot.send_message(message.from_user.id, 'Упс, произошла ошибка. Возвращаю в главное меню.')
                message.text = '🔙 Главное меню'
                return get_text_messages(message)

        markup.add(f'Показать еще {msg_count} ?', '🔙 Главное меню')
        msg = bot.reply_to(message, 'Показать еще или вернуться в главное меню? 💬', reply_markup=markup)
        bot.register_next_step_handler(msg, query_data, qs_generator, msg_count)

    def send_message(user_id, query):
        if query.new_price:
            if query.new_price > query.base_price:
                new_price = f'{query.new_price} 🔺'
            else:
                new_price = f'{query.new_price} ❗️ ⬇️ 🔥'
        else:
            new_price = 'Нет'

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Добавить в избранное', callback_data=f'{query.id_item},{query.cat_id}'))
        bot.send_message(user_id, f'<b>{query.title}</b>'
                                  f'\nСтартовая цена: {query.base_price}'
                                  f'\nНовая цена: {new_price}'
                                  f'\nГород: {query.city}'
                                  f'\nПродано: {"Да" if query.deleted else "Нет"}'
                                  f'\nДата в объявлении: {query.date}'
                                  f'\nСсылка: {query.url}',
                         parse_mode='HTML', reply_markup=markup)

        sleep(0.1)
        logger.info('Bot send_message')

    def get_category_from_bd(message):
        try:
            category = Category.objects.get(name=message.text)
        except Category.DoesNotExist as ex:
            bot.send_message(message.from_user.id, '*Упс, проблема с категорией* 💬', parse_mode="Markdown")
            logger.error(f'{ex} in get_category_from_bd')
        return category.pk

    bot.polling(none_stop=True, interval=0)
