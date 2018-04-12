#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Filters, CommandHandler, CallbackQueryHandler)
from tgcnbot.extensions import db
from tgcnbot.user.models import save_user, User
from tgcnbot.chat.models import Chat, ChatUser


def mygroups(bot, update):
    from_user = None
    if hasattr(update, 'message') and getattr(update, 'message'):
        from_user = update.message.from_user
    if hasattr(update, 'callback_query') and getattr(update, 'callback_query'):
        from_user = update.callback_query.from_user
    if not from_user:
        return
    user = User.query.get(from_user.id)  # 暂无群组
    groups = Chat.query\
        .filter(db.or_(Chat.type == 'group', Chat.type == 'supergroup'))\
        .join(ChatUser, ChatUser.chat_id == Chat.id)\
        .filter(ChatUser.user_id == user.id)\
        .all()
    content = u'选择群组'
    buttons = []
    for index, group in enumerate(groups):
        button = InlineKeyboardButton(
            group.title, callback_data='group:{}'.format(group.id))
        if index % 2 == 0:
            button_row = [button, ]
            buttons.append(button_row)
        else:
            buttons[index / 2].append(button)

    if hasattr(update, 'message') and getattr(update, 'message'):
        update.message.reply_text(
            content, reply_markup=InlineKeyboardMarkup(buttons))
    if hasattr(update, 'callback_query') and getattr(update, 'callback_query'):
        update.callback_query.edit_message_text(
            content, reply_markup=InlineKeyboardMarkup(buttons))


def group_settings(bot, update):
    group_id = update.callback_query.data.split('group:')[-1]
    chat = Chat.query.get(group_id)
    if not chat:
        bot.sendMessage(update.callback_query.chat.id, u'无此群组')
    content = u'群组设置'
    buttons = [
        [
            InlineKeyboardButton(
                '删除入群信息',
                callback_data='group:del_join_msg:{}'.format(group_id)),
            InlineKeyboardButton(
                '禁止发贴纸',
                callback_data='group:fb_send_sticker:{}'.format(group_id))],
        [
            InlineKeyboardButton(
                '禁止发文件',
                callback_data='group:fb_send_doc:{}'.format(group_id)), ],
        [
            InlineKeyboardButton(
                '« 返回群组列表',
                callback_data='mygroups'), ],
    ]

    update.callback_query.edit_message_text(
        text=content,
        reply_markup=InlineKeyboardMarkup(buttons))


handlers = [
    CommandHandler('mygroups', mygroups),
    CallbackQueryHandler(mygroups, pattern='mygroups'),
    CallbackQueryHandler(group_settings, pattern='group:'), ]
