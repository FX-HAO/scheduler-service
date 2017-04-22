from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
from ..minixs import CRUDMixin, Serializer


class User(CRUDMixin, Serializer, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    sina = db.relationship('Sina', backref='follower', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def reset_password(self, password):
        self.password = password
