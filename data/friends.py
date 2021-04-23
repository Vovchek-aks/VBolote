import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# класс друзей


class Friends(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    u_id1 = sqlalchemy.Column(sqlalchemy.Integer)
    u_id2 = sqlalchemy.Column(sqlalchemy.Integer)

    # users = orm.relation("users")



