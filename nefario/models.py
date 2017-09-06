from flask import abort

from . import db
from .utils import timestamp


class User(db.Model):
    """The User model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Integer, default=timestamp)
    updated_at = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    last_seen_at = db.Column(db.Integer, default=timestamp)
    nickname = db.Column(db.String(32), nullable=False, unique=True)
    token = db.Column(db.String(64), nullable=True, unique=True)

    @staticmethod
    def create(data):
        """Create a new user."""
        user = User()
        user.from_dict(data, partial_update=False)
        return user

    def from_dict(self, data, partial_update=True):
        """Import user data from a dictionary."""
        for field in ['nickname']:
            try:
                setattr(self, field, data[field])
            except KeyError:
                if not partial_update:
                    abort(400)
