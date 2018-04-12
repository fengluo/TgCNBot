from datetime import datetime
from tgcnbot.extensions import db
from tgcnbot.utils.database import CRUDMixin


def save_user(user_data):
    user = User.query.get(user_data.id)
    if not user:
        user = User(id=user_data.id)
    user.username = user_data.username
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.language_code = user_data.language_code
    user.save()
    return user


class User(db.Model, CRUDMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    language_code = db.Column(db.String(15))
    # role = db.Column(db.String(15))
    # until_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chats = db.relationship(
        'ChatUser',
        primaryjoin="User.id == ChatUser.user_id",
        foreign_keys='ChatUser.user_id',
        back_populates='user')
