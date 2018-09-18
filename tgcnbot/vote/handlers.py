import re
import operator
from datetime import datetime, timedelta
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Filters, CommandHandler, CallbackQueryHandler,
                          MessageHandler, ConversationHandler)
from tgcnbot.vote.models import Vote, Joiner
from tgcnbot.user.models import save_user
from tgcnbot.chat.models import ChatUser
from tgcnbot.extensions import db


def report(bot, update, job_queue):
    reply_to_message = update.message.reply_to_message
    if not reply_to_message:
        # Todo
        # 删除信息，回复提醒需要使用 report 命令回复举报信息；15秒后自动删除
        reply = update.message.reply_text(
            '{} 请用 /report 回复需要举报的消息方可生效'.format(
                update.message.from_user.name))
        update.message.delete()
        if reply:
            job_queue.run_once(
                delete_message,
                10,
                context=(reply.chat.id, reply.message_id))
        return
    # Todo 把这里整理出方法
    chat_id = reply_to_message.chat.id
    # message_id = update.message.message_id
    target_message_id = reply_to_message.message_id
    target_user_id = reply_to_message.from_user.id
    text = reply_to_message.text
    target_user = save_user(reply_to_message.from_user)
    chat_user = ChatUser.query.filter(
        ChatUser.chat_id == chat_id,
        ChatUser.user_id == target_user_id
    ).first()
    if chat_user and chat_user.status in ['administrator', 'creator']:
        reply = update.message.reply_text(
            '{} 无法举报管理员'.format(
                update.message.from_user.name))
        update.message.delete()
        if reply:
            job_queue.run_once(
                delete_message,
                10,
                context=(reply.chat.id, reply.message_id))
        return
    vote = Vote.query.filter(
        Vote.chat_id == chat_id,
        Vote.target_message_id == target_message_id).first()
    if vote:
        update.message.delete()
        return
    vote = Vote(
        chat_id=chat_id,
        # message_id=message_id,
        target_user_id=target_user_id,
        target_message_id=target_message_id,
        text=text)
    vote.save()
    content = \
        """
该消息被举报，下面进入表决。
Bot 将会统计5分钟内的投票。

Spam 消息：被举报成员将会被 Bot 踢出群组；
违反群规：被举报成员将会被禁言10小时；
取消表决：该举报无效。

任一投票选项需要至少3票才能被算作有效。
滥用者会被管理员踢出群组。
管理员对此结果拥有最终解释权和懒得解释权。
"""
    buttons = [
        [
            InlineKeyboardButton(
                'Spam 消息 0',
                callback_data='report:spam'),
            InlineKeyboardButton(
                '违反群规 0',
                callback_data='report:break'),
            InlineKeyboardButton(
                '取消表决 0',
                callback_data='report:cancel')],
    ]
    message = bot.sendMessage(
        chat_id=update.message.chat.id,
        reply_to_message_id=update.message.reply_to_message.message_id,
        text=content,
        parse_mode='html',
        reply_markup=InlineKeyboardMarkup(buttons))

    vote.message_id = message.message_id
    vote.save()
    update.message.delete()
    job_queue.run_once(
        result,
        300,
        context=vote.id)


def delete_message(bot, job):
    bot.delete_message(*job.context, timeout=10)


def result(bot, job):
    vote = Vote.query.get(job.context)
    vote.status = 0
    vote.save()
    spam_tickets_num = len(vote.spam_tickets)
    break_tickets_num = len(vote.break_tickets)
    cancel_tickets_num = len(vote.cancel_tickets)
    total_tickets_num = len(vote.joiners)
    ratios = {}
    if total_tickets_num:
        if cancel_tickets_num >= 3:
            ratios['cancel'] = float(cancel_tickets_num / total_tickets_num)
        if break_tickets_num >= 3:
            ratios['break'] = float(break_tickets_num / total_tickets_num)
        if spam_tickets_num >= 3:
            ratios['spam'] = float(spam_tickets_num / total_tickets_num)
        ticket_name = 'cancel'
        if len(ratios.items()) > 0:
            ticket_name = max(ratios.items(), key=operator.itemgetter(1))[0]
    else:
        ticket_name = 'cancel'
    if ticket_name == 'spam':
        bot.delete_message(
            chat_id=vote.chat_id,
            message_id=vote.target_message_id
        )
        bot.kick_chat_member(
            chat_id=vote.chat_id,
            user_id=vote.target_user_id)
    if ticket_name == 'break':
        bot.delete_message(
            chat_id=vote.chat_id,
            message_id=vote.target_message_id
        )
        bot.restrict_chat_member(
            chat_id=vote.chat_id,
            user_id=vote.target_user_id,
            until_date=datetime.now()+timedelta(hours=10),
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
        )
    results = {
        'spam': 'Spam 消息\n该用户将被踢出群组。',
        'break': '违反群规\n该用户将被禁言10小时。',
        'cancel': ' 取消表决'
    }
    content = \
        """
对 {} 所发消息投票统计如下：\n
1. Spam 消息 {}票\n
2. 违反群规 {}票\n
3. 取消表决 {}票\n
投票结果为：{}\n
管理员对此结果拥有最终解释权和懒得解释权。
""".format(
            vote.target_user.name,
            spam_tickets_num,
            break_tickets_num,
            cancel_tickets_num,
            results[ticket_name])
    print(content)
    bot.editMessageText(
        chat_id=vote.chat_id,
        message_id=vote.message_id,
        text=content
    )


def vote(bot, update):
    print(update.callback_query)
    reply_to_message = update.callback_query.message.reply_to_message
    callback_data = update.callback_query.data
    chat_id = reply_to_message.chat.id
    target_message_id = reply_to_message.message_id
    vote = Vote.query.filter(
        Vote.chat_id == chat_id,
        Vote.target_message_id == target_message_id).first()
    if not vote or not vote.status:
        return
    user = save_user(update.callback_query.from_user)
    report_type = next(iter(re.findall(r":([a-z]+)", callback_data)), None)

    joiner = Joiner.query.filter(
        Joiner.user == user,
        Joiner.vote == vote).first()
    if not joiner:
        joiner = Joiner(user=user, vote=vote, ticket=report_type)
        joiner.save()
    elif joiner.ticket == report_type:
        joiner.delete()
    else:
        joiner.ticket = report_type
        joiner.save()

    db.session.flush()
    # vote = Vote.query.filter(
    #     Vote.chat_id == chat_id,
    #     Vote.target_message_id == target_message_id).first()

    for joiner in vote.joiners:
        print(joiner.vote_id, joiner.user_id, joiner.ticket)
    spam_tickets_num = Joiner.query.filter(
        Joiner.vote_id == vote.id,
        Joiner.ticket == 'spam'
    ).count()
    break_tickets_num = Joiner.query.filter(
        Joiner.vote_id == vote.id,
        Joiner.ticket == 'break'
    ).count()
    cancel_tickets_num = Joiner.query.filter(
        Joiner.vote_id == vote.id,
        Joiner.ticket == 'cancel'
    ).count()
    print('spam ', spam_tickets_num)
    print('break ', break_tickets_num)
    print('cancel ', cancel_tickets_num)
    buttons = [
        [
            InlineKeyboardButton(
                'Spam 消息 {}'.format(spam_tickets_num),
                callback_data='report:spam'),
            InlineKeyboardButton(
                '违反群规 {}'.format(break_tickets_num),
                callback_data='report:break'),
            InlineKeyboardButton(
                '取消表决 {}'.format(cancel_tickets_num),
                callback_data='report:cancel')],
    ]
    update.callback_query.edit_message_reply_markup(
        # text="该消息被举报，下面进入表决。",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return 1


handlers = [
    CommandHandler('report', report, pass_job_queue=True),
    CallbackQueryHandler(vote, pattern='report:')
]
