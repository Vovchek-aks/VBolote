from flask import Flask, redirect, render_template, request, abort, make_response, jsonify
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime as dt
from forms.login import LoginForm
from forms.register import RegisterForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).filter(User.email == form.email.data).first()
#         if user and user.check_password(form.password.data):
#             login_user(user, remember=form.remember_me.data)
#             return redirect("/")
#         return render_template('login.html',
#                                message="Неправильный логин или пароль",
#                                form=form)
#     return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         if form.password.data != form.password_again.data:
#             return render_template('register.html', title='Регистрация',
#                                    form=form,
#                                    message="Пароли не совпадают")
#         db_sess = db_session.create_session()
#         if db_sess.query(User).filter(User.email == form.email.data).first():
#             return render_template('register.html', title='Регистрация',
#                                    form=form,
#                                    message="Такой пользователь уже есть")
#         user = User(
#             name=form.name.data,
#             email=form.email.data,
#             sex=form.sex.data,
#             age=form.age.data,
#             sexual_orientation=form.sexual_orientation.data,
#             about=form.about.data,
#             au_attitude=form.au_attitude.data,
#             frog_attitude=form.frog_attitude.data,
#             cvc_code=form.cvc_code.data,
#             # modified_date=dt.date.today()
#         )
#         user.set_password(form.password.data)
#         db_sess.add(user)
#         db_sess.commit()
#         login_user(user, remember=True)
#         return redirect('/')
#     return render_template('register.html', title='Регистрация', form=form)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/user.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
