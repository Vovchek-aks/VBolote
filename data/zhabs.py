import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Zhaba(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'zhabs'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    pw = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    u_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)

    # jobs = orm.relation("Job")


