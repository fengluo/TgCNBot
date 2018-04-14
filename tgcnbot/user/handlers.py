#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
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
            buttons[int(index / 2)].append(button)

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
        bot.sendMessage(update.callback_query.chat.id, '无此群组')
    content = '{} 群组设置'.format(chat.title)
    buttons = [
        [
            InlineKeyboardButton(
                '删除入群信息',
                callback_data='group:{}:del_join_msg'.format(group_id)),
            InlineKeyboardButton(
                '禁止发贴纸',
                callback_data='group:{}:fb_send_sticker'.format(group_id))],
        [
            InlineKeyboardButton(
                '禁止发文件',
                callback_data='group:{}:fb_send_doc'.format(group_id)), ],
        [
            InlineKeyboardButton(
                '« 返回群组列表',
                callback_data='mygroups'), ],
    ]

    update.callback_query.edit_message_text(
        text=content,
        reply_markup=InlineKeyboardMarkup(buttons))
    return 2


settings = {
    'del_join_msg': '删除入群消息',
    'fb_send_sticker': '禁止发贴纸',
    'fb_send_doc': '禁止发文档'
}

values = {
    0: '关闭',
    1: '开启'
}


def process_group_setting(bot, update):
    group_id = next(
        iter(re.findall(r":(-\d*)", update.callback_query.data)), None)
    key = next(
        iter(re.findall(r":([a-z]\w*)", update.callback_query.data)), None)
    value = next(iter(re.findall(r":(\d)", update.callback_query.data)), None)
    chat = Chat.query.get(group_id)
    if not chat:
        bot.sendMessage(update.callback_query.chat.id, '无此群组')
        return
    if hasattr(chat, key) and value is not None:
        setattr(chat, key, value)
        chat.save()
    content = '{} {}: {}'.format(
        chat.title,
        settings.get(key),
        values.get(int(getattr(chat, key) or 0)))
    buttons = [
        [
            InlineKeyboardButton(
                values.get(int(not int(getattr(chat, key) or 0))),
                callback_data='group:{}:{}:{}'.format(
                    group_id,
                    key,
                    int(not int(getattr(chat, key) or 0)))), ],
        [InlineKeyboardButton(
            '« 返回设置', callback_data='group:{}'.format(group_id)), ]
    ]
    update.callback_query.edit_message_text(
        text=content,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return 1


handlers = [
    CommandHandler('mygroups', mygroups),
    CallbackQueryHandler(mygroups, pattern='mygroups'),
    CallbackQueryHandler(process_group_setting, pattern='^group:-(\d*):(\w*)'),
    CallbackQueryHandler(group_settings, pattern='^group:-(\d*)'), ]
