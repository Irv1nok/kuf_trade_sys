import logging
from collections import Counter

from bot.middlewares import get_query

from parser.models import Category, KufarItems
from bot.models import BotUser, FavoritesItems

from bot.keyboards.replykeyoboards import load_reply_keyboard_back_gen_menu, load_reply_keyboard_with_gen_menu_and_next

from bot.services import send_error_msg_not_registered, send_message

from bot.bot_config import user_data, bot_sub_menu, bot

from telebot import types

logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    if BotUser.objects.filter(telegram_id=message.from_user.id).exists():  # Проверяем регистрацию пользователя
        user_data.user_registered = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Компьютерная техника 🖥')
    btn2 = types.KeyboardButton('Телефоны и планшеты 📱')
    # btn3 = types.KeyboardButton('Все для детей и мам 🛍')
    # btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
    # btn5 = types.KeyboardButton('Авто и транспорт 🚗')

    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "👋 Вас приветствует Kufar Bot", reply_markup=markup)
    bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел')


@bot.message_handler(commands=['favorites'])
def show_favorites(message):
    """Избранное"""
    markup = load_reply_keyboard_back_gen_menu()
    if user_data.user_registered:
        try:
            qs = BotUser.objects.get(telegram_id=message.from_user.id).favoritesitems_set.all()
            if qs.count() == 0:
                bot.send_message(message.from_user.id, text='🗣Список пуст.. ', reply_markup=markup)
            else:
                bot.send_message(message.from_user.id, text='🗣 Вот список:', reply_markup=markup)
                for q in qs:
                    item = KufarItems.objects.get(pk=q.pk_item)
                    send_message(user_id=message.from_user.id,
                                 item=item,
                                 favorites=True,
                                 user_registered=user_data.user_registered)

        except Exception as ex:
            logger.error(f'{ex} in show_favorites func')
            bot.send_message(message.from_user.id, text='🗣 Ошибка! 😔 Попробуйте еще раз.'
                                                        '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help'
                                                        '\nВозвращаю в главное меню. 🔙 ')
            message.text = '🔙 Главное меню'
            get_text_messages(message)
    else:
        send_error_msg_not_registered(message)


@bot.message_handler(commands=['register'])
def register_user(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    if not BotUser.objects.filter(telegram_id=message.from_user.id).exists():
        bot.send_message(message.from_user.id, text='🗣 Здорово!👏 Я рад что вы решили зарегестрироваться. '
                                                    'Это позволит вам добавлять товары в избранное, '
                                                    'а я буду следить за этими товарами и если '
                                                    'они подешевеют или будут проданы,'
                                                    'я отправлю вам сообщение. 👍'
                                                    '\n\n🗣 Так же!, в разделе *Ищу*, вы можете настроить '
                                                    'поиск товара и я сообщу, если такой появиться ❗️',
                         parse_mode='Markdown')
        markup.add('Да', 'Нет')
        bot.send_message(message.from_user.id, '🗣 Зарегестрироваться? 💬', reply_markup=markup, parse_mode='HTML')
        bot.register_next_step_handler(message, register_user_step2)
    else:
        btn = types.KeyboardButton('🔙 Главное меню')
        markup.add(btn)
        bot.send_message(chat_id=message.from_user.id,
                         text='🗣 Вы уже зарегестрированы 👍'
                              '\nЕсли вы видите это сообщение после регистрации,'
                              '\n*перезапустите бота* в меню комманд /start 🆙',
                         reply_markup=markup,
                         parse_mode='Markdown')


def register_user_step2(message):
    try:
        BotUser.objects.create(telegram_id=message.from_user.id, name=message.from_user.first_name)
        bot.send_message(message.from_user.id, text='🗣 Успешно! 👍'
                                                    '\nПерезапускаю бота..'
                                                    '\nВозвращаю в главное меню. 🔙 ')
    except Exception as ex:
        logger.error(f'{ex} in register_user_step3')
        bot.send_message(message.from_user.id, text='🗣 Ошибка! 😔 Попробуйте еще раз.'
                                                    '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help'
                                                    '\nВозвращаю в главное меню. 🔙 ')
    finally:
        message.text = '/start'
        start(message)


@bot.message_handler(commands=['account'])
def account(message):
    if not user_data.user_registered:
        send_error_msg_not_registered(message)
    else:
        markup = load_reply_keyboard_back_gen_menu()

        user = BotUser.objects.get(telegram_id=message.from_user.id)
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Мой *ID*:  {user.telegram_id}'
                              f'\n*Имя*:  {user.name}',
                         reply_markup=markup,
                         parse_mode='Markdown')


@bot.message_handler(commands=['search'])
def add_search_items(message):
    pass


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.from_user.id,
                     text='🗣 Бот находится в стадии разработки,'
                          '\nв случае любых сложностей перезапустите бота'
                          '\nили свяжитесь с разработчиком --> @Irvin_ok ,'
                          '\nв сообщении опишите цепочку действий, которая'
                          '\nпривела к сообщению об ошибке.'
                          '\nТак же принимаются пожелания по улучшению.',
                     parse_mode="HTML")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
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
        user_data.category = get_category_from_bd(message)
        btn1 = types.KeyboardButton('Показать объявления')
        btn2 = types.KeyboardButton('Поиск по фильтру')
        btn3 = types.KeyboardButton('Показать проданные объявления')
        btn4 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        bot.send_message(message.from_user.id, '🗣 Выберите пункт меню.',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_query)

    elif message.text == '🔙 Главное меню':
        user_data.category = None
        btn1 = types.KeyboardButton('Компьютерная техника 🖥')
        btn2 = types.KeyboardButton('Телефоны и планшеты 📱')
        # btn3 = types.KeyboardButton('Все для детей и мам 🛍')
        # btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
        # btn5 = types.KeyboardButton('Авто и транспорт 🚗')
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('fav'))
def callback_favorites(call):
    """Обработка нажатий на инлайн клавиатуру(Добавить/удалить из Избранного)"""
    if call.data:
        cat, op, pk = call.data.split(',')
        user = BotUser.objects.get(telegram_id=call.from_user.id)
        if op == 'add':
            try:
                user.favoritesitems_set.create(pk_item=int(pk))
                KufarItems.objects.filter(pk=int(pk)).update(in_favorites=True)
                bot.send_message(chat_id=call.from_user.id, text='Готово')
            except Exception as ex:
                bot.send_message(chat_id=call.from_user.id,
                                 text='🗣 Ошибка!. Попробуйте еще раз.'
                                      '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help')
                logger.error(f'{ex} in callback_favorites func')

        elif op == 'delete':
            try:
                item = FavoritesItems.objects.get(pk_item=int(pk))
                user.favoritesitems_set.remove(item)
                item.delete()

                obj = KufarItems.objects.get(pk=int(pk))
                cnt = Counter([FavoritesItems.objects.values_list('pk_item')])
                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                # Проверяем есть у др.пользователей товар в избранном
                if cnt[str(obj.pk)] <= 1:
                    # Если нету, снимаем флаг c товара. Сделано для оптимизации запросов,
                    # что бы при парсинге данных не делать запрос в бд на каждом объявлении.
                    KufarItems.objects.filter(pk=int(pk)).update(in_favorites=False)

                show_favorites(message=call)  # Возврат в главное меню
            except Exception:
                bot.send_message(chat_id=call.from_user.id,
                                 text='🗣 Ошибка! Возможно товар уже *удален*.'
                                      '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help')


@bot.callback_query_handler(func=lambda call: call.data.startswith('title'))
def callback_title_inlinekeyboard(call):
    f, cat, name = call.data.split('|')
    user_data.title = name
    bot.send_message(chat_id=call.from_user.id, text='Готово. Нажмите далее.', reply_markup=load_reply_keyboard_with_gen_menu_and_next())


@bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
def callback_city_inlinekeyboard(call):
    f, name = call.data.split('|')
    user_data.city = name
    bot.send_message(chat_id=call.from_user.id, text='Готово. Нажмите далее.', reply_markup=load_reply_keyboard_with_gen_menu_and_next())


def get_category_from_bd(message):
    try:
        category = Category.objects.get(name=message.text)
    except Category.DoesNotExist as ex:
        bot.send_message(message.from_user.id, '🗣 *Упс, проблема с категорией* 💬', parse_mode="Markdown")
        logger.error(f'{ex} in get_category_from_bd')
    return category.pk


bot_command_menu = {'/start': start, '/favorites': show_favorites, '/register': register_user,
                    '/account': account, '/help': show_help,
                    '🔙 Главное меню': get_text_messages}
