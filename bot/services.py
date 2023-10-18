import logging

from bot.models import BotUser, Items
from parser.models import Category, KufarItems
from django.db.utils import IntegrityError
from time import sleep

from decouple import config

from telebot import TeleBot, types

logger = logging.getLogger(__name__)


def start_bot():
    bot = TeleBot(config('BOT_TOKEN'))
    bot_sub_menu = ['Ноутбуки', 'Компьютеры', 'Мониторы', 'Телефоны', 'Планшеты', 'Процессоры', 'Оперативная память',
                    'Материнские платы', 'Кулеры', 'Корпуса', 'Жесткие диски', 'Видеокарты', 'Блоки питания',
                    'SSD', 'Фотопринтеры', 'Сканеры', 'Принтеры', 'МФУ']

    category = None
    user_registered = False

    def load_reply_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = types.KeyboardButton('🔙 Главное меню')
        markup.add(btn)
        return markup

    @bot.message_handler(commands=['start'])  # стартовая команда
    def start(message):
        if BotUser.objects.filter(telegram_id=message.from_user.id).exists():
            nonlocal user_registered
            user_registered = True
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
        markup = load_reply_keyboard()
        if user_registered:
            try:
                qs = BotUser.objects.get(telegram_id=message.from_user.id).items_set.all()
                if qs.count() == 0:
                    bot.send_message(message.from_user.id, text='🗣Список пуст.. ', reply_markup=markup)
                else:
                    bot.send_message(message.from_user.id, text='🗣 Вот список:', reply_markup=markup)
                    for q in qs:
                        item = KufarItems.objects.get(pk=q.pk_item)
                        send_message(user_id=message.from_user.id, item=item, favorites=True)

            except Exception as ex:
                logger.error(f'{ex} in show_favorites func')
                bot.send_message(message.from_user.id, text='🗣 Упс!. Ошибка! 😔 '
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
            bot.send_message(message.from_user.id, text='🗣 Упс!. Ошибка! 😔 '
                                                        '\nВозвращаю в главное меню. 🔙 ')
        finally:
            message.text = '/start'
            start(message)

    @bot.message_handler(commands=['account'])
    def account(message):
        if not user_registered:
            send_error_msg_not_registered(message)
        else:
            markup = load_reply_keyboard()

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
                              '\nили свяжитесь с разработчиком --> @Irvin_ok',
                         parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data:
            op, pk = call.data.split(',')
            user = BotUser.objects.get(telegram_id=call.from_user.id)
            if op == 'add':
                try:
                    user.items_set.create(pk_item=int(pk))
                except IntegrityError:
                    try:
                        item = Items.objects.get(pk_item=int(pk))
                        user.items_set.add(item)
                    except Exception:
                        bot.send_message(chat_id=call.from_user.id,
                                         text='🗣 Упс!. Ошибка!.'
                                              'Если ошибка повториться свяжитесь с'
                                              ' разработчиком.', parse_mode='Markdown')
                except Exception as ex:
                    logger.error(f'{ex} in callback_worker func')

            elif op == 'delete':
                try:
                    item = Items.objects.get(pk_item=int(pk))
                    user.items_set.remove(item)
                    show_favorites(message=call)
                except Exception:
                    bot.send_message(chat_id=call.from_user.id, text='🗣 Упс!. Ошибка! Возможно товар уже *удален*.'
                                                                     'Если ошибка ошибка повториться свяжитесь с'
                                                                     ' разработчиком.', parse_mode='Markdown')

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
            bot.send_message(message.from_user.id, '🗣 Сколько объявлений показать?'
                                                   '\nВыберите, или введите в чат *число:*',
                             reply_markup=markup,
                             parse_mode="Markdown")
            bot.register_next_step_handler(message, get_query_params)

        elif message.text == '🔙 Главное меню':
            category = None
            btn1 = types.KeyboardButton('Компьютерная техника 🖥')
            btn2 = types.KeyboardButton('Телефоны и планшеты 📱')
            # btn3 = types.KeyboardButton('Все для детей и мам 🛍')
            # btn4 = types.KeyboardButton('Хобби, спорт и туризм 🎿')
            # btn5 = types.KeyboardButton('Авто и транспорт 🚗')
            markup.add(btn1, btn2)
            bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

    def send_error_msg_not_registered(message):
        markup = load_reply_keyboard()
        bot.send_message(chat_id=message.from_user.id,
                         text='🗣 Вы еще не зарегестрированы 👀'
                              '\nЗарегестрируйтесь, чтобы начать пользоваться..'
                              '\nЕсли вы видите это сообщение после регистрации,'
                              '\n*перезапустите бота* в меню комманд /start 🆙',
                         reply_markup=markup,
                         parse_mode='Markdown')

    def get_query_params(message):
        if msg := bot_command_menu.get(message.text):
            return msg(message)
        try:
            msg_count = int(message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Да', 'Нет')
            deleted = bot.reply_to(message, '🗣 Показать проданные объявления? 💬', reply_markup=markup)
            bot.register_next_step_handler(deleted, get_query_data, msg_count)
        except ValueError:
            msg_count = bot.reply_to(message, '🗣 *Ошибка! Введите число. Повторите ввод:* 💬', parse_mode="Markdown")
            bot.register_next_step_handler(msg_count, get_query_params)

    def get_query_data(message, msg_count):
        del_obj = True if message.text == 'Да' else False

        qs = KufarItems.objects.filter(cat_id=category).filter(deleted=del_obj).order_by(
            '-date' if not del_obj else "-time_create")
        qs_generator = init_qs_generator(qs)
        query_data(message, qs_generator, msg_count)

    def init_qs_generator(qs):
        for q in qs:
            yield q

    def query_data(message, qs_generator, msg_count):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if msg := bot_command_menu.get(message.text):
            return msg(message)

        count = 0
        while count != msg_count:
            try:
                query = next(qs_generator)
                send_message(user_id=message.from_user.id, item=query)
                count += 1
            except Exception as ex:
                logger.error(f'Exception - {ex} in show_query_data')
                bot.send_message(message.from_user.id, '🗣 Упс, произошла ошибка. Возвращаю в главное меню.')
                message.text = '🔙 Главное меню'
                return get_text_messages(message)

        markup.add(f'Показать еще {msg_count}', '🔙 Главное меню')
        msg = bot.reply_to(message, '🗣 Показать еще или вернуться в главное меню? 💬', reply_markup=markup)
        bot.register_next_step_handler(msg, query_data, qs_generator, msg_count)

    def send_message(user_id, item, favorites=False):
        nonlocal user_registered
        if item.new_price:
            if item.new_price > item.base_price:
                new_price = f'{item.new_price} 🔺'
            else:
                new_price = f'{item.new_price} ❗️ ⬇️ 🔥'
        else:
            new_price = 'Нет'

        if user_registered:
            markup = types.InlineKeyboardMarkup()
            if not favorites:
                markup.add(types.InlineKeyboardButton('Добавить в избранное',
                                                      callback_data=f'add,{item.pk}'))
            else:
                markup.add(types.InlineKeyboardButton('Удалить из избранного',
                                                      callback_data=f'delete,{item.pk}'))

        bot.send_message(user_id, f'<b>{item.title}</b>'
                                  f'\nСтартовая цена: {item.base_price}'
                                  f'\nНовая цена: {new_price}'
                                  f'\nГород: {item.city}'
                                  f'\nПродано: {"Да" if item.deleted else "Нет"}'
                                  f'\nДата в объявлении: {item.date}'
                                  f'\nСсылка: {item.url}',
                         parse_mode='HTML',
                         reply_markup=markup if user_registered else None)

        sleep(0.1)
        logger.info('Bot send_message')

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

    bot.polling(none_stop=True, interval=0)
