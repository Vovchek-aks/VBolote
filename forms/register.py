from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    # sex = StringField('Пол пользователя*', validators=[DataRequired()])
    # age = IntegerField('Возраст*')
    # about = StringField('О себе*')
    # au_attitude = StringField('Отношение к Андрею Юрьевичу')
    # frog_attitude = StringField('Отношение к лягушкам и жабам*')
    # cvc_code = StringField('CVC вашей карты*')
    submit = SubmitField('Зарегестрироваться в Болоте')

