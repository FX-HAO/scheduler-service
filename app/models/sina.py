# coding: utf-8
from .. import db
from ..minixs import CRUDMixin, Serializer

class Sina(CRUDMixin, Serializer, db):
    __tablename__ = 'sina'
    id = db.Column(db.Integer, primary_key=True)
    sina_id = db.Column(db.Integer, index=True, unique=True)
    username = db.Column(db.String(1, 64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))