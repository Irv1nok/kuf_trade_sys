import logging
from collections import Counter
from parser.models import Category, KufarItems

from bot.bot_config import bot, bot_sub_menu, user_data
from bot.keyboards.inlinekeyboards import inline_keyboard_delete_search_item
from bot.keyboards.replykeyoboards import (reply_keyboard_back_gen_menu,
                                           reply_keyboard_back_gen_menu_and_next)
from bot.middlewares import get_category_from_bd, get_query
from bot.models import BotUser, FavoritesItems, SearchItems
from bot.services import send_error_msg_not_registered, send_message

from django.db import IntegrityError

from telebot import types

logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    if BotUser.objects.filter(telegram_id=message.from_user.id).exists():  # Проверяем регистрацию пользователя
        user_data.user_registered = True
    else:
        user_data.user_registered = False
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Компьютерная техника. 🖥')
    btn2 = types.KeyboardButton('Телефоны и планшеты. 📱')
    btn3 = types.KeyboardButton('Строительный инструмент. 🛠')

    markup.row(btn1, btn2)
    markup.row(btn3)
    bot.send_message(message.from_user.id, f"*{message.from_user.first_name}*. Вас приветствует 👋 Kufar Bot",
                     reply_markup=markup, parse_mode='Markdown')
    bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел')


@bot.message_handler(commands=['favorites'])
def show_favorites(message):
    """Избранное"""
    markup = reply_keyboard_back_gen_menu()
    if user_data.user_registered:
        try:
            qs = BotUser.objects.get(telegram_id=message.from_user.id).favoritesitems_set.all()
            if not qs.exists():
                bot.send_message(message.from_user.id, text='💬 Список пуст.. ', reply_markup=markup)
            else:
                bot.send_message(message.from_user.id, text='💬 Вот список:', reply_markup=markup)
                for q in qs:
                    item = KufarItems.objects.get(pk=q.pk_item)
                    send_message(user_id=message.from_user.id,
                                 obj=item,
                                 favorites=True)

        except Exception as ex:
            logger.error(f'Error --{ex}-- in show_favorites func')
            bot.send_message(message.from_user.id, text='💬 Ошибка! 😔 Попробуйте еще раз.'
                                                        '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help'
                                                        '\nВозвращаю в главное меню. 🔙 ')
            message.text = '🔙 Главное меню'
            get_text_messages(message)
    else:
        send_error_msg_not_registered(message)


@bot.message_handler(commands=['register'])
def register_user(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if not user_data.user_registered:
        try:
            BotUser.objects.get(telegram_id=message.from_user.id)
            btn = types.KeyboardButton('🔙 Главное меню')
            markup.add(btn)
        except Exception:
            bot.send_message(message.from_user.id, text='💬 Здорово!👏 Я рад что вы решили зарегестрироваться. '
                                                        'Это позволит вам добавлять товары в избранное, '
                                                        'а я буду следить за этими товарами и если '
                                                        'они подешевеют или будут проданы,'
                                                        'я отправлю вам сообщение. 👍'
                                                        '\n\n💬 Так же!, в разделе *Задать авто.поиск..*, вы можете настроить '
                                                        'поиск товара и я сообщу, если такой появиться ❗️',
                             parse_mode='Markdown')
            markup.add('Да', 'Нет')
            bot.send_message(message.from_user.id, '💬 Зарегестрироваться? ', reply_markup=markup, parse_mode='HTML')
            bot.register_next_step_handler(message, register_user_step2)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text='💬 Вы уже зарегестрированы 👍'
                                  '\nЕсли вы видите это сообщение после регистрации,'
                                  '\n*перезапустите бота* в меню комманд /start 🆙',
                             reply_markup=markup,
                             parse_mode='Markdown')
    else:
        bot.send_message(chat_id=message.from_user.id,
                         text='💬 Вы уже зарегестрированы 👍')


def register_user_step2(message):
    if message.text == 'Да':
        try:
            BotUser.objects.create(telegram_id=message.from_user.id, name=message.from_user.first_name)
            bot.send_message(message.from_user.id, text='💬 Успешно! 👍'
                                                        '\nПерезапускаю бота..'
                                                        '\nВозвращаю в главное меню. 🔙 ')
        except Exception as ex:
            logger.exception(f'Error --{ex}-- in register_user_step2')
            bot.send_message(message.from_user.id, text='💬 Ошибка! 😔 Попробуйте еще раз.'
                                                        '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. '
                                                        '/help'
                                                        '\nВозвращаю в главное меню. 🔙 ')
        finally:
            message.text = '/start'
            start(message)
    else:
        bot.send_message(message.from_user.id, text='💬 Сожалею! '
                                                    '\nПерезапускаю бота..'
                                                    '\nВозвращаю в главное меню. 🔙 ')
        message.text = '/start'
        start(message)


@bot.message_handler(commands=['account'])
def account(message):
    if not user_data.user_registered:
        send_error_msg_not_registered(message)
    else:
        markup = reply_keyboard_back_gen_menu()

        user = BotUser.objects.get(telegram_id=message.from_user.id)
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Мой ID:  *{user.telegram_id}*'
                              f'\nИмя:  *{user.name}*'
                              f'\nСлоты для избранных товаров: *{user.slots_for_favitems}*'
                              f'\nСлоты для поиска: *{user.slots_for_searchitems}*',
                         reply_markup=markup,
                         parse_mode='Markdown')


@bot.message_handler(commands=['search'])
def search_items(message):
    markup = reply_keyboard_back_gen_menu()
    if not user_data.user_registered:
        send_error_msg_not_registered(message)
    else:
        try:
            user = BotUser.objects.get(telegram_id=int(message.from_user.id))
            if user.searchitems_set.exists():
                for obj in user.searchitems_set.all():
                    cat = Category.objects.get(pk=obj.category).name
                    title = obj.title if obj.title else "Не задано"
                    min_price = obj.min_price if obj.min_price else "Не задано"
                    max_price = obj.max_price if obj.max_price else "Не задано"
                    city = obj.city if obj.city else "Не задано"
                    state = 'Новое' if obj.state else 'Б/У' if obj.state is not None else 'Любое'

                    bot.send_message(message.from_user.id, f'⚙️ *Категория* - {cat}'
                                                           f'\n👀 *Название* - {title}'
                                                           f'\n⬇️ *Мин.цена* - {min_price}'
                                                           f'\n⬆️ *Макс.цена* - {max_price}'
                                                           f'\n🌏 *Город* - {city}'
                                                           f'\n💎 *Состояние* - {state}',
                                     reply_markup=inline_keyboard_delete_search_item(obj.pk), parse_mode='Markdown')

                bot.send_message(message.from_user.id, 'Выберите пункт меню', reply_markup=markup)
            else:
                bot.send_message(message.from_user.id, '💬 Список пуст..', reply_markup=markup)
        except Exception as ex:
            bot.send_message(message.from_user.id, '💬 Ошибка! 😔 Попробуйте еще раз.'
                                                   '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help',
                             reply_markup=markup)
            logger.exception(f'Error --{ex}-- in search_items handler')


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.from_user.id,
                     text='💬 Бот находится в стадии разработки, '
                          'в случае любых сложностей перезапустите бота '
                          'или свяжитесь с разработчиком --> @Irv1n_TM, '
                          'в сообщении опишите цепочку действий, которая '
                          'привела к сообщению об ошибке. '
                          'Так же принимаются пожелания по улучшению.',
                     parse_mode="HTML")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == 'Компьютерная техника. 🖥':
        btn1 = types.KeyboardButton('Ноутбуки. 💻')
        btn2 = types.KeyboardButton('Компьютеры. 📺')
        btn3 = types.KeyboardButton('Мониторы. 🖥')
        btn4 = types.KeyboardButton('Комплектующие. ⚙️')
        btn5 = types.KeyboardButton('Оргтехника. 🖨')
        btn9 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        markup.row(btn5, btn9)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    elif message.text == 'Строительный инструмент. 🛠':
        btn1 = types.KeyboardButton('Бензо и электрорезы. ⚙️')
        btn2 = types.KeyboardButton('Дрели. 🔫')
        btn3 = types.KeyboardButton('Измерительный инструмент. 📐')
        btn4 = types.KeyboardButton('Ключи, отвертки. 🪛')
        btn5 = types.KeyboardButton('Краскораспылители, краскопульты. 🚿')
        btn6 = types.KeyboardButton('Кусачки, плоскогубцы, пассатижи. 🛠')
        btn7 = types.KeyboardButton('Лобзики. 🪚')
        btn8 = types.KeyboardButton('Миксеры строительные. 🧬')
        btn9 = types.KeyboardButton('Наборы инструментов. 🛠')
        btn10 = types.KeyboardButton('Ножницы по металлу. 💎')
        btn11 = types.KeyboardButton('Отбойные молотки, топоры, кувалды. 🔨')
        btn12 = types.KeyboardButton('Паяльники. 🚬')
        btn13 = types.KeyboardButton('Перфораторы. ⚡️')
        btn14 = types.KeyboardButton('Пистолеты для клея, пены, герметиков. 🔫️')
        btn15 = types.KeyboardButton('Плиткорезы, стеклорезы, захваты. 🪚')
        btn16 = types.KeyboardButton('Рубанки. 🪚')
        btn17 = types.KeyboardButton('Степлеры, гвоздезабиватели. 🔨')
        btn18 = types.KeyboardButton('Тиски. 💽')
        btn19 = types.KeyboardButton('Фены строительные. ⚡️')
        btn20 = types.KeyboardButton('Фрезеры. 💳')
        btn21 = types.KeyboardButton('Шлифовальные машины, болгарки. ⚡️')
        btn22 = types.KeyboardButton('Шпатели, валики, кисти. 📽')
        btn23 = types.KeyboardButton('Шуруповерты. ⚡️')
        btn24 = types.KeyboardButton('Ведра, емкости. 🪣')
        btn25 = types.KeyboardButton('Оснастка для инструмента. 🛠')
        btn26 = types.KeyboardButton('Циркулярные, сабельные пилы. ⚙')
        btn27 = types.KeyboardButton('Ящики, сумки для инструментов. 🧰')
        btn28 = types.KeyboardButton('Прочие инструменты. 🧰')
        btn29 = types.KeyboardButton('🔙 Главное меню')

        markup.add(btn1, btn2, btn3)
        markup.add(btn4, btn5, btn6)
        markup.add(btn7, btn8, btn9)
        markup.add(btn10, btn11, btn12)
        markup.add(btn13, btn14, btn15)
        markup.add(btn16, btn17, btn18)
        markup.add(btn19, btn20, btn21)
        markup.add(btn22, btn23, btn24)
        markup.add(btn25, btn26, btn27)
        markup.add(btn28, btn29)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    elif message.text == 'Телефоны и планшеты. 📱':
        btn1 = types.KeyboardButton('Телефоны. 📱')
        btn2 = types.KeyboardButton('Планшеты. 🕹')
        btn3 = types.KeyboardButton('Умные часы и фитнес-трекеры. ⌚️')
        btn4 = types.KeyboardButton('Наушники. 🎧')
        btn5 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        markup.row(btn5)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    elif message.text == 'Комплектующие. ⚙️':
        btn1 = types.KeyboardButton('Процессоры. 💎')
        btn2 = types.KeyboardButton('Оперативная память. 💳')
        btn3 = types.KeyboardButton('Материнские платы. 🎛')
        btn4 = types.KeyboardButton('Видеокарты. 📽')
        btn5 = types.KeyboardButton('Блоки питания. ⚡️')
        btn6 = types.KeyboardButton('SSD. 📼')
        btn7 = types.KeyboardButton('Кулеры. 🌡')
        btn8 = types.KeyboardButton('Корпуса. 📦')
        btn9 = types.KeyboardButton('Жесткие диски. 💽')
        btn10 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2, btn3)
        markup.row(btn4, btn5, btn6)
        markup.row(btn7, btn8, btn9)
        markup.row(btn10)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    elif message.text == 'Оргтехника. 🖨':
        btn1 = types.KeyboardButton('МФУ. 📠')
        btn2 = types.KeyboardButton('Принтеры. 🖨')
        btn3 = types.KeyboardButton('Сканеры. 📷')
        btn4 = types.KeyboardButton('Фотопринтеры. 📸')
        btn5 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2, btn3)
        markup.row(btn4, btn5)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    elif message.text == 'Наушники. 🎧':
        btn1 = types.KeyboardButton('Внутриканальные. 🎧')
        btn2 = types.KeyboardButton('Вкладыши. 🎧')
        btn3 = types.KeyboardButton('Накладные. 🎧')
        btn4 = types.KeyboardButton('Полноразмерные. 🎧')
        btn5 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2, btn3)
        markup.row(btn4, btn5)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    elif message.text in bot_sub_menu:
        user_data.category = get_category_from_bd(message)
        btn1 = types.KeyboardButton('Показать объявления 🪧')
        btn2 = types.KeyboardButton('Поиск по фильтру 🔎')
        btn3 = types.KeyboardButton('Показать проданные объявления 💸')
        btn4 = types.KeyboardButton('Узнать цену 📊')
        btn5 = types.KeyboardButton('Задать авто. поиск по параметрам 📩')
        btn6 = types.KeyboardButton('🔙 Главное меню')
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        markup.row(btn5, btn6)
        bot.send_message(message.from_user.id, '💬 Выберите пункт меню.',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_query)

    elif message.text == '🔙 Главное меню':
        user_data.category = None
        btn1 = types.KeyboardButton('Компьютерная техника. 🖥')
        btn2 = types.KeyboardButton('Телефоны и планшеты. 📱')
        btn3 = types.KeyboardButton('Строительный инструмент. 🛠')
        markup.row(btn1, btn2)
        markup.row(btn3)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('fav'))
def callback_favorites_inline(call):
    """ Обработка нажатий на инлайн клавиатуру(Добавить/удалить из Избранного) """
    if call.data:
        cat, op, pk = call.data.split('|')
        user = BotUser.objects.get(telegram_id=call.from_user.id)
        if op == 'add' and user.slots_for_favitems > 0:
            try:
                user.favoritesitems_set.create(pk_item=int(pk))
                KufarItems.objects.filter(pk=int(pk)).update(in_favorites=True)
                user.slots_for_favitems -= 1
                user.save(update_fields=['slots_for_favitems'])
                bot.send_message(chat_id=call.from_user.id, text=f'💬 Готово, осталось слотов {user.slots_for_favitems}')
            except IntegrityError as ex:
                bot.send_message(chat_id=call.from_user.id,
                                 text='💬 Ошибка!. Товар уже добавлен'
                                      '\nЕсли это ошибка, свяжитесь с разработчиком. /help')
                logger.error(f'Error --{ex}-- in callback_fav_inline')

            except Exception as ex:
                bot.send_message(chat_id=call.from_user.id,
                                 text='💬 Ошибка!. Попробуйте еще раз.'
                                      '\nВозможно у вас закончились свободные слоты.'
                                      '\nЕсли ошибка повториться свяжитесь с разработчиком. /help')
                logger.exception(f'{ex} in callback_favorites func')

        elif op == 'add' and user.slots_for_favitems == 0:
            bot.send_message(chat_id=call.from_user.id,
                             text='💬 У вас закончились свободные слоты.'
                                  '\nЕсли это ошибка свяжитесь с разработчиком. /help')

        elif op == 'delete':
            try:
                item = FavoritesItems.objects.get(pk_item=int(pk))
                item.delete()
                user.slots_for_favitems += 1
                user.save(update_fields=['slots_for_favitems'])
                # Считаем по pk_item количество совпадений во всех избранных товарах
                obj = KufarItems.objects.get(pk=int(pk))
                cnt = Counter([FavoritesItems.objects.values_list('pk_item')])
                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                # Проверяем есть у др.пользователей товар в избранном
                if cnt[str(obj.pk)] <= 1:
                    # Если нету, снимаем флаг c товара. Сделано для оптимизации запросов,
                    # что бы при парсинге данных не делать запрос в бд на каждом объявлении.
                    KufarItems.objects.filter(pk=int(pk)).update(in_favorites=False)

                bot.send_message(chat_id=call.from_user.id, text=f'💬 Готово, доступно слотов {user.slots_for_favitems}')
            except Exception:
                bot.send_message(chat_id=call.from_user.id,
                                 text='💬 Ошибка! Возможно товар уже *удален*.'
                                      '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help')


@bot.callback_query_handler(func=lambda call: call.data.startswith('title'))
def callback_title_inline(call):
    f, cat, name = call.data.split('|')
    user_data.title = name
    bot.send_message(chat_id=call.from_user.id, text='💬 Готово. Нажмите далее.',
                     reply_markup=reply_keyboard_back_gen_menu_and_next())


@bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
def callback_city_inline(call):
    f, name = call.data.split('|')
    user_data.city = name
    bot.send_message(chat_id=call.from_user.id, text='💬 Готово. Нажмите далее.',
                     reply_markup=reply_keyboard_back_gen_menu_and_next())


@bot.callback_query_handler(func=lambda call: call.data.startswith('search'))
def callback_search_inline(call):
    f, op, pk = call.data.split('|')
    user = BotUser.objects.get(telegram_id=call.from_user.id)
    obj = SearchItems.objects.get(pk=pk)
    obj.delete()
    user.slots_for_searchitems += 1
    user.save(update_fields=['slots_for_searchitems'])
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    bot.send_message(chat_id=call.from_user.id, text=f'💬 Готово, доступно слотов {user.slots_for_searchitems}')
