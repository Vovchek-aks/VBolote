from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class EditUserForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = StringField('О себе')
    au_attitude = StringField('Отношение к Андрею Юрьевичу')
    frog_attitude = StringField('Отношение к лягушкам и жабам')
    submit = SubmitField('Принять изменения')
