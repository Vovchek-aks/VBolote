from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    text = TextAreaField('Текст жабей вести', validators=[DataRequired()])
    submit = SubmitField('Отжабить')
