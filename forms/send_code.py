from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class CodeForm(FlaskForm):
    code = StringField('Код', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
