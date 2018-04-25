import re
import operator
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Filters, CommandHandler, CallbackQueryHandler,
                          MessageHandler, ConversationHandler)
from tgcnbot.vote.models import Vote, Joiner
from tgcnbot.user.models import save_user


def report(bot, update, job_queue):
    print(update.message)
    reply_to_message = update.message.reply_to_message
    if not reply_to_message:
        # Todo
        # 删除信息，回复提醒需要使用 report 命令回复举报信息；15秒后自动删除
        return
    #Todo 把这里整理出方法
    chat_id = reply_to_message.chat.id
    # message_id = update.message.message_id
    target_message_id = reply_to_message.message_id
    target_user_id = reply_to_message.from_user.id
    text = reply_to_message.text
    vote = Vote.query.filter(
        Vote.chat_id == chat_id,
        Vote.target_message_id == target_message_id).first()
    if vote:
        return
    vote = Vote(
        chat_id=chat_id,
        # message_id=message_id,
        target_user_id=target_user_id,
        target_message_id=target_message_id,
        text=text)
    vote.save()
    content = "该消息被举报，下面进入表决。"
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
        reply_markup=InlineKeyboardMarkup(buttons))
    print(message.message_id)
    vote.message_id = message.message_id
    vote.save()
    update.message.delete()
    job_queue.run_once(
        result,
        10,
        context=vote.id)


def result(bot, job):
    vote = Vote.query.get(job.context)
    spam_tickets_num = len(vote.spam_tickets)
    break_tickets_num = len(vote.break_tickets)
    cancel_tickets_num = len(vote.cancel_tickets)
    total_tickets_num = len(vote.joiners)
    ratios = {}
    ratios['spam'] = int(spam_tickets_num / total_tickets_num)
    ratios['break'] = int(break_tickets_num / total_tickets_num)
    ratios['cancel'] = int(cancel_tickets_num / total_tickets_num)
    ticket_name = max(ratios.items(), key=operator.itemgetter(1))[0]
    results = {
        'spam': 'Spam 消息',
        'break': '违反群规',
        'cancel': ' 取消表决'
    }
    content = \
    """
    对 {} 所发消息投票统计如下：\n
    1. Spam 消息 {}票\n
    2. 违反群规 {}票\n
    3. 取消表决 {}票\n
    投票结果为：{}
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
    if not vote:
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

    vote = Vote.query.filter(
        Vote.chat_id == chat_id,
        Vote.target_message_id == target_message_id).first()

    for joiner in vote.joiners:
        print(joiner.vote_id, joiner.user_id, joiner.ticket)
    
    buttons=[
        [
            InlineKeyboardButton(
                'Spam 消息 {}'.format(len(vote.spam_tickets)),
                callback_data='report:spam'),
            InlineKeyboardButton(
                '违反群规 {}'.format(len(vote.break_tickets)),
                callback_data='report:break'),
            InlineKeyboardButton(
                '取消表决 {}'.format(len(vote.cancel_tickets)),
                callback_data='report:cancel')],
    ]
    update.callback_query.edit_message_text(
        text="该消息被举报，下面进入表决。",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return 1


handlers = [
    CommandHandler('report', report, pass_job_queue=True),
    CallbackQueryHandler(vote, pattern='report:')
]
