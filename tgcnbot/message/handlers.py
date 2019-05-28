import re
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Filters, CommandHandler, CallbackQueryHandler,
                          MessageHandler, ConversationHandler)
from tgcnbot.extensions import db
from tgcnbot.chat.models import save_chat, get_chats, Chat, ChatUser
from tgcnbot.user.models import save_user, User


def process_new_chat_members(bot, update):
    new_chat_members = update.message.new_chat_members
    if not new_chat_members:
        return
    chat = Chat.query.get(update.message.chat.id)
    for new_chat_member in new_chat_members:
        if new_chat_member.id == bot.id:
            chat = save_chat(update.message.chat)
            print(chat.id)
            admins = bot.getChatAdministrators(chat.id)
            for admin in admins:
                user = save_user(admin.user)
                chat_user = ChatUser.query.filter(
                    ChatUser.user_id == user.id,
                    ChatUser.chat_id == chat.id).first()
                if not chat_user:
                    chat_user = ChatUser(
                        chat=chat,
                        user=user)
                chat_user.status = admin.status
                chat_user.until_date = admin.until_date
                chat.users.append(chat_user)
                chat.save()

    if chat.del_join_msg:
        update.message.delete()


def delete_message(bot, job):
    bot.delete_message(*job.context)


def process_filter_message(bot, update, job_queue):
    group_id = update.message.chat.id
    chat = Chat.query.get(group_id)
    if not chat:
        bot.sendMessage(group_id, '请重新加 bot 到群组')
        return
    message_type = '文件'
    reply = None
    if update.message.sticker and chat.fb_send_sticker:
        message_type = u'贴纸'
        reply = update.message.reply_text(
            '{} 请看群规。本群禁止发{}。'.format(
                update.message.from_user.name,
                message_type))
        update.message.delete()
    if update.message.document and chat.fb_send_doc:
        message_type = u'文件'
        reply = update.message.reply_text(
            '{} 请看群规。本群禁止发{}。'.format(
                update.message.from_user.name,
                message_type))
        update.message.delete()
    if update.message.forward_from_message_id and chat.fb_send_forward:
        message_type = '转发内容'
        reply = update.message.reply_text(
            '{} 请看群规。本群禁止发{}。'.format(
                update.message.from_user.name,
                message_type))
        update.message.delete()

    if reply:
        job_queue.run_once(
            delete_message,
            15,
            context=(reply.chat.id, reply.message_id))


def check_content(content):
    forbidden_words = [
        '://ais',
        'www.ais',
        '增粉',
        '拉粉',
        'XackerTVHD'
    ]
    def filter_word(word):
        return re.search(word, content)
    return len(list(filter(filter_word, forbidden_words)))

# The temporary function
def process_filter_photo(bot, update, job_queue):
    message = update.message or update.edited_message
    group_id = message.chat.id
    chat = Chat.query.get(group_id)
    if not chat:
        bot.sendMessage(group_id, '请重新加 bot 到群组')
        return
    reply = None
    caption = message.caption

    if caption and check_content(caption) or \
        update.edited_message and update.edited_message.caption and update.edited_message.caption.startswith('http://t.cn'):
        reply = message.reply_text(
            '{} 发现敏感内容。'.format(
                message.from_user.name))
        bot.kick_chat_member(group_id, message.from_user.id)
        message.delete()
    if reply:
        job_queue.run_once(
            delete_message,
            15,
            context=(reply.chat.id, reply.message_id))


handlers = [
    MessageHandler(
        Filters.group & Filters.status_update.new_chat_members,
        process_new_chat_members),
    MessageHandler(
        Filters.group & (Filters.document | Filters.sticker),
        process_filter_message, pass_job_queue=True),
    MessageHandler(
        Filters.group & (Filters.photo | Filters.forwarded),
        process_filter_photo, pass_job_queue=True, edited_updates=True)
]
