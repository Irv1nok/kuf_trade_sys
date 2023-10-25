import logging

from bot.bot_config import user_data
from bot.keyboards.replykeyoboards import load_reply_keyboard_back_gen_menu

from decouple import config

from telebot import TeleBot, types


logger = logging.getLogger(__name__)
bot = TeleBot(config('BOT_TOKEN'))

def send_error_msg_not_registered(message):
    markup = load_reply_keyboard_back_gen_menu()
    bot.send_message(chat_id=message.from_user.id,
                     text='🗣 Вы еще не зарегестрированы 👀'
                          '\nЗарегестрируйтесь, чтобы начать пользоваться..'
                          '\nЕсли вы видите это сообщение после регистрации,'
                          '\n*перезапустите бота* в меню комманд /start 🆙',
                     reply_markup=markup,
                     parse_mode='Markdown')


def send_message(user_id: int, item,
                 user_registered: bool,
                 show_sold_items: bool = False,
                 update_message: bool = False,
                 favorites: bool = False,
                 ):
    if item.new_price:
        if item.new_price > item.base_price:
            new_price = f'{item.new_price} 🔺'
        else:
            new_price = f'{item.new_price} ❗️ ⬇️ 🔥'
    else:
        new_price = 'Нет'

    if user_data.user_registered:
        markup = types.InlineKeyboardMarkup()
        if not show_sold_items:
            if not favorites:
                markup.add(types.InlineKeyboardButton('Добавить в избранное',
                                                      callback_data=f'fav,add,{item.pk}'))
            else:
                markup.add(types.InlineKeyboardButton('Удалить из избранного',
                                                      callback_data=f'fav,delete,{item.pk}'))

    noimage_photo = open('bot/static/noimage.jpg', 'rb')
    if update_message:
        bot.send_message(user_id, '🔥❗️❗ Изменение цены в объявлении.  ❗❗🔥️')
    bot.send_photo(chat_id=user_id,
                   photo=item.photo_url if item.photo_url and not show_sold_items else noimage_photo,
                   caption=f'<b>{item.title}</b>'
                           f'\nСтартовая цена: {item.base_price}'
                           f'\nНовая цена: {new_price}'
                           f'\nГород: {item.city}'
                           f'\nПродано: {"Да" if item.deleted else "Нет"}'
                           f'\nДата в объявлении: {item.date}'
                           f'\nСсылка: {item.url}',
                   parse_mode='HTML',
                   reply_markup=markup if user_registered else None)

    if update_message:
        bot.send_message(user_id, '🔥❗️❗ Изменение цены в объявлении.  ❗❗🔥️')

    logger.info('Bot send_message')