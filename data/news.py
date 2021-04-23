import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# класс, отвечающий за новости

class News(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    u_id = sqlalchemy.Column(sqlalchemy.Integer)

    dislikes = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    text = sqlalchemy.Column(sqlalchemy.String)

    # users = orm.relation("users")


