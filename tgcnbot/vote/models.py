from datetime import datetime
from sqlalchemy.util import hybridproperty
from tgcnbot.extensions import db
from tgcnbot.utils.database import CRUDMixin

def save_vote(data):
    vote = Vote.query.filter(
        Vote.chat_id == data.chat.id,
        Vote.message_id == data.message_id).first()
    if not vote:
        vote = Vote(
            chat_id=data.chat.id,
            message_id=data.message_id,
            text=data.text)
        vote.save()
    return vote

class Joiner(db.Model, CRUDMixin):
    __tablename__ = 'joiner'
    vote_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(50))
    user = db.relationship(
        'User',
        primaryjoin="Joiner.user_id==User.id",
        foreign_keys='Joiner.user_id')


class Vote(db.Model, CRUDMixin):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)
    message_id = db.Column(db.Integer)
    target_message_id = db.Column(db.Integer)
    target_user_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship(
        'Chat',
        primaryjoin="Chat.id == Vote.chat_id",
        foreign_keys='Vote.chat_id',
        backref='votes')

    target_user = db.relationship(
        'User',
        primaryjoin='User.id == Vote.target_user_id',
        foreign_keys='Vote.target_user_id',
        backref='target_votes'
    )
    
    users = db.relationship(
        'User',
        # secondary="join(User, Joiner.user_id == User.id)",
        secondary='joiner',
        primaryjoin='Vote.id == foreign(Joiner.vote_id)',
        secondaryjoin='foreign(Joiner.user_id) == User.id',
        foreign_keys='[Joiner.vote_id, Joiner.user_id]',
        backref='votes')
    
    joiners = db.relationship(
        'Joiner',
        primaryjoin='Vote.id == Joiner.vote_id',
        foreign_keys='Joiner.vote_id',
        backref="vote")

    spam_tickets = db.relationship(
        'Joiner',
        primaryjoin='and_(Vote.id == Joiner.vote_id, Joiner.ticket == "spam")',
        foreign_keys='Joiner.vote_id')
   
    break_tickets = db.relationship(
        'Joiner',
        primaryjoin='and_(Vote.id == Joiner.vote_id, Joiner.ticket == "break")',
        foreign_keys='Joiner.vote_id')

    cancel_tickets = db.relationship(
        'Joiner',
        primaryjoin='and_(Vote.id == Joiner.vote_id, Joiner.ticket == "cancel")',
        foreign_keys='Joiner.vote_id')
