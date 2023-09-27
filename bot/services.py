from parser.models import Category, KufarItems

from decouple import config

from django.utils import timezone

from telebot import TeleBot, types


def start_bot():
    tz = timezone.get_default_timezone()
    cat = None
    bot = TeleBot(config('BOT_TOKEN'))

    @bot.message_handler(commands=['start'])  # стартовая команда
    def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Компьютерная техника")
        btn2 = types.KeyboardButton('Телефоны и планшеты')
        btn3 = types.KeyboardButton('Все для детей и мам')
        btn4 = types.KeyboardButton('Хобби, спорт и туризм')
        btn5 = types.KeyboardButton('Авто и транспорт')

        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id, "👋 Вас приветствует Kufar bot", reply_markup=markup)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел')

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        nonlocal cat
        if message.text == 'Компьютерная техника':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Ноутбуки")
            btn2 = types.KeyboardButton('Компьютеры')
            btn3 = types.KeyboardButton('Мониторы')
            btn4 = types.KeyboardButton('Комплектующие')
            btn9 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn2, btn3, btn4, btn9)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Телефоны и планшеты':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Телефоны")
            btn2 = types.KeyboardButton('Планшеты')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Телефоны':
            cat = get_category_from_bd(message)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Получить новые объявления")
            # btn2 = types.KeyboardButton('Далее ->')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Планшеты':
            cat = get_category_from_bd(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Получить новые объявления")
            # btn2 = types.KeyboardButton('Далее ->')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Ноутбуки':
            cat = get_category_from_bd(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Получить новые объявления")
            # btn2 = types.KeyboardButton('Далее ->')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Компьютеры':
            cat = get_category_from_bd(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Получить новые объявления')
            # btn2 = types.KeyboardButton('Настроить фильтр')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Мониторы':
            cat = get_category_from_bd(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Получить новые объявления')
            # btn2 = types.KeyboardButton('Настроить фильтр')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Комплектующие':
            cat = get_category_from_bd(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Получить новые объявления')
            # btn2 = types.KeyboardButton('Настроить фильтр')
            btn3 = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn1, btn3)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

        elif message.text == 'Получить новые объявления':
            count = bot.reply_to(message, 'Сколько объявлений показать? Введите число:')
            bot.register_next_step_handler(count, get_query_params)

        elif message.text == '🔙 Главное меню':
            cat = None
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Компьютерная техника")
            btn2 = types.KeyboardButton('Телефоны и планшеты')
            btn3 = types.KeyboardButton('Все для детей и мам')
            btn4 = types.KeyboardButton('Хобби, спорт и туризм')
            btn5 = types.KeyboardButton('Авто и транспорт')
            markup.add(btn1, btn2, btn3, btn4, btn5)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    def get_query_params(message):
        try:
            parms = int(message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Нет')
            deleted = bot.reply_to(message, 'Показать проданные объявления?', reply_markup=markup)
            bot.register_next_step_handler(deleted, get_query_data, parms)
        except ValueError:
            msg_count = bot.reply_to(message, 'Ошибка! Введите число. Повторите ввод:')
            bot.register_next_step_handler(msg_count, get_query_params)
            return

    def get_query_data(message, parms):
        msg_count = parms
        del_obj = True if message.text == 'Да' else False

        query = KufarItems.objects.filter(cat_id=cat).filter(deleted=del_obj).order_by('time_update')[:msg_count]
        for q in query:
            bot.send_message(message.from_user.id, f'<b>{q.title}</b>'
                                                   f'\nСтартовая цена: {q.base_price}'
                                                   f'\nНовая цена: {q.new_price if q.new_price else "Нет"}'
                                                   f'\nГород: {q.city}'
                                                   f'\nПродано: {"Да" if q.deleted else "Нет"}'
                                                   f'\nДата в объявлении: {q.date}'
                                                   f'\nДата обновления бд: {q.time_update.astimezone(tz).strftime("%d.%m.%Y %H:%M")}'
                                                   f'\nСсылка: {q.url}',
                             parse_mode='HTML')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Получить новые объявления', '🔙 Главное меню')
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    def get_category_from_bd(message):
        try:
            category = Category.objects.get(name=message.text)
        except Category.DoesNotExist:
            bot.send_message(message.from_user.id, 'Упс, проблема с категорией')
        return category.pk

    bot.polling(none_stop=True, interval=0)
