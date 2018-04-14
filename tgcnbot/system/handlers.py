#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Filters, CommandHandler)
from tgcnbot.user.models import save_user, User


def start(bot, update):
    from_user = update.message.from_user
    save_user(from_user)
    update.message.reply_text('我是 @tgcnbot 群组辅助机器人')


def myinfo(bot, update):
    from_user = update.message.from_user
    content = 'id: {}\nfirst name: {}\nlast name: {}\nusername: {}'.format(
        from_user.id,
        from_user.first_name,
        from_user.last_name,
        from_user.username)
    update.message.reply_text(content)


handlers = [
    CommandHandler('start', start, ~Filters.group),
    CommandHandler('myinfo', myinfo, ~Filters.group), ]
