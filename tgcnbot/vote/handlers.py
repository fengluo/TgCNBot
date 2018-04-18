import re
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Filters, CommandHandler, CallbackQueryHandler,
                          MessageHandler, ConversationHandler)


def report(bot, update):
    print(update.message)
    if not update.message.reply_to_message:
        # Todo
        # 删除信息，回复提醒需要使用 report 命令回复举报信息；15秒后自动删除
        return
    content = "该消息被举报，下面进入表决。"
    buttons = [
        [
            InlineKeyboardButton(
                'Spam 消息',
                callback_data='report:spam'),
            InlineKeyboardButton(
                '违反群规',
                callback_data='report:break'),
            InlineKeyboardButton(
                '取消表决',
                callback_data='report:cancel')],
    ]
    bot.sendMessage(
        chat_id=update.message.chat.id,
        reply_to_message_id=update.message.reply_to_message.message_id,
        text=content,
        reply_markup=InlineKeyboardMarkup(buttons))
    update.message.delete()


def process_report(bot, update):
    print(update.callback_query)
    callback_data = update.callback_query.data
    report_type = next(iter(re.findall(r":([a-z]+)", callback_data)), None)
    buttons=[
        [
            InlineKeyboardButton(
                'Spam 消息',
                callback_data='report:spam'),
            InlineKeyboardButton(
                '违反群规',
                callback_data='report:break'),
            InlineKeyboardButton(
                '取消表决',
                callback_data='report:cancel')],
    ]
    update.callback_query.edit_message_text(
        text="该消息被举报，下面进入表决。",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return 1


handlers = [
    CommandHandler('report', report),
    CallbackQueryHandler(process_report, pattern='report:')
]
