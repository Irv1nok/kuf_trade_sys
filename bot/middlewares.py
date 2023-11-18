import logging
import time

from parser.models import KufarItems

from bot.bot_config import bot, keyboards_cats, user_data
from bot.models import BotUser
from bot.services import send_error_msg_not_registered

from bot.keyboards.inlinekeyboards import inline_keyboard_city
from bot.keyboards.replykeyoboards import (reply_keyboard_back_gen_menu,
                                           reply_keyboard_with_gen_menu_and_next,
                                           reply_keyboard_gen_menu)

from django.db.models import Q

from telebot import types

from bot.services import send_message

logger = logging.getLogger(__name__)


def get_query(message):
    user_data.reset_data()
    if message.text == '🔙 Главное меню':
        markup = reply_keyboard_gen_menu()
        return bot.send_message(message.from_user.id, '👀 *Выберите* интересующий вас раздел',
                                reply_markup=markup, parse_mode='Markdown')

    if message.text == 'Показать проданные объявления':
        user_data.deleted = True
        markup_inline = keyboards_cats[user_data.category]
        bot.send_message(message.from_user.id, '💬 *Введите* название товара или *выберите*.',
                         reply_markup=markup_inline, parse_mode='Markdown')
        markup = reply_keyboard_with_gen_menu_and_next()
        bot.send_message(message.from_user.id, 'Чтобы пропустить нажмите *Далее*',
                         reply_markup=markup, parse_mode='Markdown')
        bot.register_next_step_handler(message, get_title)

    elif message.text == 'Поиск по фильтру':
        markup_inline = keyboards_cats[user_data.category]
        bot.send_message(message.from_user.id, '💬 *Введите* название товара или выберите.',
                         reply_markup=markup_inline, parse_mode='Markdown')
        markup = reply_keyboard_with_gen_menu_and_next()
        bot.send_message(message.from_user.id, 'Чтобы пропустить нажмите *Далее*',
                         reply_markup=markup, parse_mode='Markdown')
        bot.register_next_step_handler(message, get_title)

    elif message.text == 'Задать автоматический поиск по параметрам':
        markup = reply_keyboard_gen_menu()
        user = BotUser.objects.get(telegram_id=message.from_user.id)
        if user_data.user_registered:
            if user.slots_for_searchitems > 0:
                user_data.search_item = True
                markup_inline = keyboards_cats[user_data.category]
                bot.send_message(message.from_user.id, '💬 Введите *название* товара или выберите.',
                                 reply_markup=markup_inline, parse_mode='Markdown')
                markup = reply_keyboard_with_gen_menu_and_next()
                bot.send_message(message.from_user.id, 'Чтобы пропустить нажмите *Далее*',
                                 reply_markup=markup, parse_mode='Markdown')
                bot.register_next_step_handler(message, get_title)
            else:
                return bot.send_message(message.from_user.id, 'У вас закончились слоты для поиска', reply_markup=markup)
        else:
            return send_error_msg_not_registered(message)

    elif message.text == 'Показать объявления':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('5')
        btn2 = types.KeyboardButton('10')
        btn3 = types.KeyboardButton('15')
        btn4 = types.KeyboardButton('20')
        btn5 = types.KeyboardButton('🔙 Главное меню')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id, '💬 Сколько объявлений показать?'
                                               '\nМаксимально *20*.'
                                               '\nВыберите, или введите в чат *число:*',
                         reply_markup=markup,
                         parse_mode="Markdown")
        bot.register_next_step_handler(message, get_message_quantity)

    elif message.text:
        markup = reply_keyboard_gen_menu()
        bot.register_next_step_handler(message, get_query)
        return bot.send_message(message.from_user.id, 'Такой команды нет,'
                                                      ' 👀 Выберите интересующий вас раздел', reply_markup=markup)




def get_title(message):
    if message.text == '🔙 Главное меню':
        markup = reply_keyboard_gen_menu()
        return bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)
    markup = reply_keyboard_with_gen_menu_and_next()

    if not message.text == 'Далее':
        if not len(message.text) > 30:
            user_data.title = message.text
        else:
            bot.send_message(message.from_user.id, '💬 *Ошибка!* Название не должно превыщать 30 символов.'
                                                   ' Повторите ввод: 💬',
                             reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(message, get_title)

    bot.send_message(message.from_user.id, '💬 Введите цену товара.'
                                           '\nФормат: *Минимальная цена*(пробел)*Максимальная цена*'
                                           '\nИли выберите в меню *Далее*',
                     reply_markup=markup, parse_mode="Markdown")
    bot.register_next_step_handler(message, get_price)


def get_price(message):
    if message.text == '🔙 Главное меню':
        markup = reply_keyboard_gen_menu()
        return bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)
    markup_inline = inline_keyboard_city()

    if not message.text == 'Далее':
        try:
            markup_inline = inline_keyboard_city()
            min_price, max_price = message.text.split(' ')
            user_data.min_price = int(min_price)
            user_data.max_price = int(max_price)
            if (user_data.min_price < 0 or user_data.min_price > 20_000
                    or user_data.max_price < 0 or user_data.max_price > 20_000):
                raise ValueError
            bot.send_message(message.from_user.id, '💬 Выберите город, или нажмите *Далее*,'
                                                   '\nдля поиска по всей Беларуси.',
                             reply_markup=markup_inline, parse_mode="Markdown")
            bot.register_next_step_handler(message, get_city)
        except ValueError:
            bot.reply_to(message, '💬 *Ошибка!* Вы ввели отрицательное число или более 20_000р.'
                                  ' Повторите ввод: ')
            bot.register_next_step_handler(message, get_price)
        except Exception:
            bot.reply_to(message, '💬 *Ошибка!* Введите числа через пробел. Повторите ввод:')
            bot.register_next_step_handler(message, get_price)

    elif message.text == 'Далее':
        bot.send_message(message.from_user.id, '💬 Выберите *город*, или нажмите *Далее*,'
                                               '\nдля *поиска* по всей Беларуси.',
                         reply_markup=markup_inline, parse_mode="Markdown")
        bot.register_next_step_handler(message, get_city)


def get_city(message):
    if message.text == '🔙 Главное меню':
        markup = reply_keyboard_gen_menu()
        return bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    if not message.text == 'Далее':
        user_data.city = message.text

    if user_data.search_item:
        return save_search_data_in_db(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('5')
    btn2 = types.KeyboardButton('10')
    btn3 = types.KeyboardButton('15')
    btn4 = types.KeyboardButton('20')
    btn5 = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.from_user.id, '💬 Сколько объявлений показать?'
                                           '\nМаксимально *20*.'
                                           '\nВыберите, или введите в чат *число:*',
                     reply_markup=markup,
                     parse_mode="Markdown")

    bot.register_next_step_handler(message, get_message_quantity)


def get_message_quantity(message):
    if message.text == '🔙 Главное меню':
        markup = reply_keyboard_gen_menu()
        return bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    if message.text.isdigit():
        msg_quantity = int(message.text)
        if msg_quantity > 20 or msg_quantity < 0:
            bot.send_message(message.from_user.id, '💬 Ошибка!. Превышен лимит сообщений. Устанавливаю среднее *10*.',
                             parse_mode="Markdown")
            msg_quantity = 10
    else:
        markup = reply_keyboard_back_gen_menu()
        bot.send_message(message, '💬 *Ошибка!* Выберите или повторите ввод: ',
                         reply_markup=markup, parse_mode="Markdown")
        bot.register_next_step_handler(message, get_message_quantity)
    user_data.msg_quantity = msg_quantity
    get_query_data(message)


def get_query_data(message):
    qs = KufarItems.objects.filter(cat_id=user_data.category, deleted=user_data.deleted).order_by(
        '-date' if not user_data.deleted else "-time_create")
    filter_query = Q()
    if user_data.title:
        filter_query.add(Q(title__icontains=user_data.title), Q.AND)
    if user_data.min_price and user_data.max_price:
        filter_query.add(Q(base_price__gte=user_data.min_price, base_price__lte=user_data.max_price), Q.AND)
    if user_data.city:
        filter_query.add(Q(city__icontains=user_data.city), Q.AND)
    qs = qs.filter(filter_query)

    qs_generator = init_qs_generator(qs)
    markup = reply_keyboard_with_gen_menu_and_next()
    bot.send_message(message.from_user.id, f'💬 Найдено {qs.count()} объявлений. 👀\n\n', reply_markup=markup)
    bot.register_next_step_handler(message, query_data, qs_generator)


def query_data(message, qs_generator):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == '🔙 Главное меню':
        markup = reply_keyboard_gen_menu()
        return bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    count = 0
    while count != user_data.msg_quantity:
        try:
            query = next(qs_generator)
            send_message(user_id=message.from_user.id,
                         obj=query,
                         show_sold_items=user_data.deleted)

            count += 1
            time.sleep(0.2)
        except StopIteration:
            bot.send_message(message.from_user.id, '💬 Больше нет объявлений 👀',
                             reply_markup=reply_keyboard_back_gen_menu())
            return

        except Exception as ex:
            logger.error(f'Exception - {ex} in query_data')
            bot.send_message(message.from_user.id, '💬 *Ошибка!* Попробуйте еще раз.'
                                                   '\nЕсли ошибка ошибка повториться свяжитесь с разработчиком. /help',
                             reply_markup=reply_keyboard_back_gen_menu(), parse_mode="Markdown")

    markup.add(f'Показать еще {user_data.msg_quantity}', '🔙 Главное меню')
    msg = bot.reply_to(message, '💬 Показать еще или вернуться в главное меню? ', reply_markup=markup)
    bot.register_next_step_handler(msg, query_data, qs_generator)


def init_qs_generator(qs):
    for q in qs:
        yield q


def save_search_data_in_db(message):
    markup = reply_keyboard_gen_menu()
    try:
        user = BotUser.objects.get(telegram_id=message.from_user.id)
        user.searchitems_set.create(title=user_data.title, min_price=user_data.min_price, max_price=user_data.max_price,
                                    city=user_data.city, category=user_data.category)
        user.slots_for_searchitems -= 1
        user.save(update_fields=['slots_for_searchitems'])
        return bot.send_message(message.from_user.id, '💬 Готово. Проверьте в меню команд. '
                                                      f'Доступно слотов {user.slots_for_searchitems}'
                                                      '\n/search', reply_markup=markup)

    except Exception as ex:
        logger.error(f'exception in save_search_data {ex}')
        return bot.send_message(message.from_user.id, '💬 Ошибка. Попробуйте еще раз.', reply_markup=markup)
