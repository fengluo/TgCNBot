from datetime import datetime
from tgcnbot.extensions import db
from tgcnbot.utils.database import CRUDMixin


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)

    chat = db.relationship(
        'Chat',
        primaryjoin="Chat.id == Vote.chat_id",
        foreign_keys='Vote.chat_id',
        back_populates='votes')
