import os

from telegram.ext import (Updater, CommandHandler)

from tgcnbot import system, chat, user, message
from tgcnbot.extensions import logger, db


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def run(token=None):
    if token is None:
        token = os.getenv('TELEGRAM_TOKEN')

    updater = Updater(token)

    dp = updater.dispatcher

    for handler in system.handlers:
        dp.add_handler(handler)

    for handler in message.handlers:
        dp.add_handler(handler)

    for handler in chat.handlers:
        dp.add_handler(handler)

    for handler in user.handlers:
        dp.add_handler(handler)

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    db.create_all()
    run()
