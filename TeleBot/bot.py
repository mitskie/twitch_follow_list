from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

import config
from Main import get_info

bot = Updater(token=config.TELEGRAM_TOKEN)
dispatcher = bot.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Что бы узнать, кто сейчас стримит - просто напиши ник')


def get_user(update, context):
    login = update.message.text
    print(login)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Сейчас посмотрим...')
    try:
        live_list = get_info.GetInfo(login).get_result()
        complete_message = get_info.message_result_telegram(live_list)
        context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='HTML',
                                 disable_web_page_preview=True, text=complete_message)
    except:
        print('error')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Что-то пошло не так, попробуй еще раз')


start_handler = CommandHandler('start', start)
message_handler = MessageHandler(Filters.text & (~Filters.command), get_user)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(message_handler)

bot.start_polling()
