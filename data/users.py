import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    au_attitude = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    frog_attitude = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    cvc_code = au_attitude = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # jobs = orm.relation("Job")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
