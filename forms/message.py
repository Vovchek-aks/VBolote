from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    message = TextAreaField("Жабье сообщение", validators=[DataRequired()])
    submit = SubmitField('Отжабить')

