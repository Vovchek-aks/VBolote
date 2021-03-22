import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Job(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'jobs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creater_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    politryk_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    plan = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    ids_tovarishei = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_of_piatiletka = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    end_of_piatiletka = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    result_of_plan = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    user = orm.relation('User')

