import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

# класс, отвечающий за сообщения

class Messages(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    u_id = sqlalchemy.Column(sqlalchemy.Integer)
    b_id = sqlalchemy.Column(sqlalchemy.Integer)
    text = sqlalchemy.Column(sqlalchemy.String)

    # users = orm.relation("users")


