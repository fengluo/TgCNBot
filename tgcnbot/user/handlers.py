from telegram.ext import (Filters, CommandHandler)
from tgcnbot.user.models import save_user, User


def myinfo(bot, update):
    from_user = update.message.from_user
    content = """
        id: {}\n
        first name: {}\n
        last name: {}\n
        username: {}""".format(
        from_user.id,
        from_user.first_name,
        from_user.last_name,
        from_user.username)
    update.message.reply_text(content)


handlers = [
    CommandHandler('myinfo', myinfo, ~Filters.group), ]
