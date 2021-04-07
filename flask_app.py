from flask import Flask, redirect, render_template, request, abort, make_response, jsonify
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
import datetime as dt
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.edit_user import EditUserForm
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
    if current_user.is_authenticated:
        return redirect(f'/user/{current_user.id}')
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            # au_attitude=form.au_attitude.data,
            # frog_attitude=form.frog_attitude.data,
            # cvc_code=form.cvc_code.data,
            # modified_date=dt.date.today()
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/user/<int:user_id>')
@login_required
def user_page(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(user_id == User.id).first()
    if user:
        return render_template('user_page.html', user=user)
    else:
        abort(404)


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditUserForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(current_user.id == User.id).first()
    if form.validate_on_submit():
        user.name = form.name.data
        user.au_attitude = form.au_attitude.data
        user.frog_attitude = form.frog_attitude.data
        user.about = form.about.data
        user.id = current_user.id
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/')
    else:
        if user:
            form.name.data = user.name
            form.about.data = user.about
            form.au_attitude.data = user.au_attitude
            form.frog_attitude.data = user.frog_attitude
            return render_template('edit_user.html', user=user, form=form)
        else:
            abort(404)


@app.route('/add_friend/<int:user_id>')
@login_required
def add_friend(user_id):
    logout_user()
    return redirect(f"/users/{user_id}")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/all_users')
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('all_users.html', users=users)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/user.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
