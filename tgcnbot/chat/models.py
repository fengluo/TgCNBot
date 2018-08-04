#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from tgcnbot.extensions import db
from tgcnbot.utils.database import CRUDMixin


def save_chat(chat_data):
    chat = Chat.query.get(chat_data.id)
    if not chat:
        chat = Chat(id=chat_data.id)
    chat.type = chat_data.type
    chat.title = chat_data.title
    chat.description = chat_data.description
    chat.save()
    return chat


def get_chats(chat_id):
    pass


class ChatUser(db.Model):
    __tablename__ = 'chat_user'
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    until_date = db.Column(db.DateTime)
    user = db.relationship(
        'User',
        primaryjoin="User.id == ChatUser.user_id",
        foreign_keys='ChatUser.user_id',
        back_populates='chats')
    chat = db.relationship(
        'Chat',
        primaryjoin="Chat.id == ChatUser.chat_id",
        foreign_keys='ChatUser.chat_id',
        back_populates='users')


class Chat(db.Model, CRUDMixin):
    id = db.Column(db.Integer, primary_key=True)
    # chat_id = db.Column(db.String(15))
    type = db.Column(db.String(10))
    title = db.Column(db.String(50))
    description = db.Column(db.Text)
    del_join_msg = db.Column(db.Integer, default=0)
    fb_send_sticker = db.Column(db.Integer, default=0)
    fb_send_doc = db.Column(db.Integer, default=0)
    fb_send_forward = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship(
        'ChatUser',
        primaryjoin="Chat.id == ChatUser.chat_id",
        foreign_keys='ChatUser.chat_id',
        back_populates='chat')
