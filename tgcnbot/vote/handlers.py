from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Filters, CommandHandler, CallbackQueryHandler,
                          MessageHandler, ConversationHandler)


def report(bot, update):
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
                callback_data='report:breal'),
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
    return 1


handlers = [
    CommandHandler('report', report),
    CallbackQueryHandler(process_report, pattern='report:')
]
