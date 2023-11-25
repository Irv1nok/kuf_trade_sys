import logging

from bot.bot_config import user_data
from bot.keyboards.replykeyoboards import reply_keyboard_back_gen_menu

from decouple import config

from telebot import TeleBot, types


logger = logging.getLogger(__name__)
bot = TeleBot(config('BOT_TOKEN'))


def send_error_msg_not_registered(message):
    markup = reply_keyboard_back_gen_menu()
    bot.send_message(chat_id=message.from_user.id,
                     text='💬 Вы еще не зарегестрированы 👀'
                          '\nЗарегестрируйтесь, чтобы начать пользоваться..'
                          '\nЕсли вы видите это сообщение после регистрации,'
                          '\n*перезапустите бота* в меню комманд /start 🆙',
                     reply_markup=markup,
                     parse_mode='Markdown')


def send_message(user_id: int,
                 obj,
                 show_sold_items: bool = False,  # Режим отображения проданных товаров.
                 update_fav_message: bool = False,  # Функция вызвана из parser/services/update_data, найдено изменение цены.
                 search_item_message: bool = False,  # Функция вызвана из parser/services/update_data, найдено объявление.
                 favorites: bool = False,  # Функциия вызвана из handlers/show_favorites
                 sold_item_message: bool = False
                 ):
    """Функция отправки сообщения пользователю."""
    if obj.new_price:
        if obj.new_price > obj.base_price:
            new_price = f'{obj.new_price} 🔺'
        else:
            new_price = f'{obj.new_price} ❗️ ⬇️ 🔥'
    else:
        new_price = 'Нет'

    if user_data.user_registered:
        markup = types.InlineKeyboardMarkup()
        if not show_sold_items:
            if not favorites:
                markup.add(types.InlineKeyboardButton('Добавить в избранное',
                                                      callback_data=f'fav|add|{obj.pk}'))
            else:
                markup.add(types.InlineKeyboardButton('Удалить из избранного',
                                                      callback_data=f'fav|delete|{obj.pk}'))

    deleted = "Да" if obj.deleted else "Нет"
    url = obj.url if not show_sold_items or not obj.deleted else "Нет"
    noimage_photo = open('bot/static/noimage.jpg', 'rb')
    state = 'Б/У' if not obj.state else 'Новое'

    bot.send_photo(chat_id=user_id,
                   photo=obj.photo_url if obj.photo_url else noimage_photo,
                   caption=f'<b>{obj.title}</b>'
                           f'\nСостояние: {state}'
                           f'\nСтартовая цена: {obj.base_price}'
                           f'\nНовая цена: {new_price}'
                           f'\nГород: {obj.city}'
                           f'\nПродано: {deleted}'
                           f'\nДата в объявлении: {obj.date}'
                           f'\nСсылка: {url}',
                   parse_mode='HTML',
                   reply_markup=markup if user_data.user_registered else None)

    if update_fav_message:
        bot.send_message(user_id, '🔥📫Изменение цены в объявлении🔥️')
    if search_item_message:
        bot.send_message(user_id, '❗️📫 Найдено новое объявление.❗')
    if sold_item_message:
        bot.send_message(user_id, '❗️📫 Товар продан..💰❗'
                                  '\nОбъявление больше отслеживаться не будет. Можете удалить из избранного 🚮')

    logger.info('Bot send_message')