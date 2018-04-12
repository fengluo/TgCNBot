#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Filters, CommandHandler)
from tgcnbot.user.models import save_user, User


def start(bot, update):
    from_user = update.message.from_user
    save_user(from_user)
    update.message.reply_text(u'我是 @tgcnbot 群组辅助机器人')


handlers = [
    CommandHandler('start', start, ~Filters.group), ]
