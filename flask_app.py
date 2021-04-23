import os

from flask import Flask, redirect, render_template, request, abort, make_response, jsonify, session
from werkzeug.security import generate_password_hash
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
from forms.login import LoginForm
from forms.message import MessageForm
from forms.register import RegisterForm
from forms.edit_user import EditUserForm
from forms.send_email import EmailForm
from forms.send_code import CodeForm
from forms.make_news import NewsForm
from data.users import User
from data.friends import Friends
from data.messages import Messages
from data.news import News
from data.zhabs import Zhaba
from random import randint
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# friends manager
# класс, регулирующий действия друзей

class FM:

    # метод, который возвращает информацию о том, друзья ли эти пользователи
    @staticmethod
    def is_friends(id1, id2):
        db_sess = db_session.create_session()
        return (id2,) in db_sess.query(Friends.u_id2).filter(Friends.u_id1 == id1).all() or \
               (id1,) in db_sess.query(Friends.u_id2).filter(Friends.u_id1 == id2).all()

    # метод, который возвращает друзей пользователя
    @staticmethod
    def user_friends(u_id):
        db_sess = db_session.create_session()
        return list(map(lambda x: x[0], db_sess.query(Friends.u_id2).filter(Friends.u_id1 == u_id).all() + \
                        db_sess.query(Friends.u_id1).filter(Friends.u_id2 == u_id).all()))

    # метод, который возвращает айди контракта о дружбе
    @staticmethod
    def id_fr(id1, id2):
        db_sess = db_session.create_session()
        n1 = db_sess.query(Friends).filter(Friends.u_id1 == id1).all()
        n2 = db_sess.query(Friends).filter(Friends.u_id1 == id2).all()
        for i in n1:
            if id2 == i.u_id2:
                return i.id
        for i in n2:
            if id1 == i.u_id2:
                return i.id
        return -1


# messages manager
# класс, регулирующий действия сообщений
class MM:
    @staticmethod
    def get_ms_from_id(user_id):  # возвращает переписку
        b_id = FM.id_fr(user_id, current_user.id)
        if b_id == -1:
            return None
        db_sess = db_session.create_session()
        all_m = db_sess.query(Messages).filter(Messages.b_id == b_id).all()

        if all_m is None:
            all_m = []
        else:
            all_m = list(all_m)

        all_m.sort(key=lambda x: -x.id)
        all_m = map(lambda x: (x, x.u_id == current_user.id), all_m)
        return all_m


# Жаба менеджер
class ZhM:
    @staticmethod
    def all_zh(u_id):  # возвращает всех жаб
        db_sess = db_session.create_session()
        return db_sess.query(Zhaba).filter(Zhaba.u_id == u_id).all()


# загружает юзера
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# главная страница для зарегистрированных пользователей и новичков
@app.route('/')
@app.route('/index')
def index():
    # session.pop('email', None)
    # session.pop('password', None)
    # session.pop('ok', None)

    if current_user.is_authenticated:
        return redirect(f'/user/{current_user.id}')
    return render_template("index.html")


# обработчик входа в аккаунт
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


# первый этап регистрации через отправление кода на почту
@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    return redirect('/')
    form = EmailForm()
    if form.validate_on_submit():
        if '@mail.ru' not in form.email.data:
            return render_template('send_email.html',
                                   form=form,
                                   message="Ты читать умеешь?!")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('send_email.html',
                                   form=form,
                                   message="Такой пользователь уже есть")

        pw = generate_password_hash(form.email.data)

        session['email'] = form.email.data
        session['password'] = pw

        from_email = 'code_sender@mail.ru'
        password = ']=[-p0o9'
        to_email = form.email.data
        message = 'Здравствуйте.\n' \
                  'Это сообщение с сайта Vbolote.\n' \
                  'Если вы не пытались на нём зарегистрироваться, проигнорируйте это сообщение.\n' \
                  f'Код: {pw}\n'
        print(1)
        msg = MIMEMultipart()
        print(2)
        msg.attach(MIMEText(message, 'plain'))
        print(3)
        server = smtplib.SMTP('smtp.mail.ru: 25')
        print(4)
        server.starttls()
        print(5)
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        return redirect('/send_code')
    return render_template('send_email.html', form=form)


# ввод кода из сообщения на почту
@app.route('/send_code', methods=['GET', 'POST'])
def send_code():
    return redirect('/')
    form = CodeForm()
    if form.validate_on_submit():

        password = session.get('password', None)

        if password is not None and \
                form.code.data == password:
            session['ok'] = True
            return redirect('/register')

        session.pop('email', None)
        session.pop('ok', None)
        session.pop('password', None)
        return redirect('/')

    return render_template('send_code.html', form=form)


# обработчик регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()

        # email = session.get('email', None)
        # ok = session.get('ok', False)

        # if email is None or not ok:
        #     session.pop('email', None)
        #     session.pop('password', None)
        #     session.pop('ok', None)
        #     return redirect('/')

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

        # session.pop('email', None)
        # session.pop('password', None)
        # session.pop('ok', None)

        return redirect('/')
    return render_template('register.html', form=form)


# обработчик страницы пользователя
@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_page(user_id):
    form = NewsForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(user_id == User.id).first()
    if form.validate_on_submit():
        new = News(
            u_id=current_user.id,
            text=form.text.data
        )
        db_sess.add(new)
        db_sess.commit()
        return redirect('/')
    if user:
        news = db_sess.query(News).filter(News.u_id == user.id).all()
        return render_template('user_page.html', user=user, is_friends=FM.is_friends(current_user.id, user.id),
                               form=form,
                               news=(news[::-1] if news else []),
                               zh_c=len(ZhM.all_zh(user_id)),
                               fr_c=len(FM.user_friends(user_id))
                               )
    else:
        abort(404)


# изменение страницы пользователя
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


# обработчик добавления пользователя в друзья
@app.route('/add_friend/<int:user_id>')
@login_required
def add_friend(user_id):
    db_sess = db_session.create_session()
    fr = Friends(
        u_id1=current_user.id,
        u_id2=user_id
    )
    db_sess.add(fr)
    db_sess.commit()
    return redirect(f"/user/{user_id}")


# обработчик удаления друга (вова лох)
@app.route('/del_friend/<int:user_id>')
@login_required
def del_friend(user_id):
    db_sess = db_session.create_session()
    fr = db_sess.query(Friends).filter(Friends.id == FM.id_fr(current_user.id, user_id)).first()
    if fr:
        m = db_sess.query(Messages).filter(Messages.b_id == fr.id).all()
        if m:
            for i in m:
                db_sess.delete(i)
        db_sess.delete(fr)
        db_sess.commit()
    return redirect(f"/user/{user_id}")


# страница со всеми пользователями
@app.route('/all_users')
@login_required
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('all_users.html', users=users)


# страница выбора аватарки
@app.route('/choose_ava')
@login_required
def choose_ava():
    return render_template('choose_ava.html')


# обработчик установления аватарки для профиля
@app.route('/set_ava/<int:ava_id>')
@login_required
def set_ava(ava_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(current_user.id == User.id).first()
    user.pic = ava_id
    user.id = current_user.id
    db_sess.merge(user)
    db_sess.commit()
    return redirect('/')


# страница с друзьями указанного пользователя
@app.route('/friends/<int:user_id>')
@login_required
def friends(user_id):
    db_sess = db_session.create_session()
    fr = FM.user_friends(user_id)
    users = []
    for i in fr:
        users += db_sess.query(User).filter(User.id == i).all()
    return render_template('friends.html', users=users)


# просто скажите сайонара своему профилю :(
@app.route('/suicide')
@login_required
def suicide():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


# диалог пользователя
@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def messages(user_id):
    form = MessageForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        m = Messages(
            u_id=current_user.id,
            b_id=FM.id_fr(user_id, current_user.id),
            text=form.message.data
        )
        db_sess.add(m)
        db_sess.commit()
        return redirect(f'/messages/{user_id}')
    else:
        user = db_sess.query(User).filter(User.id == user_id).first()
        msgs = MM.get_ms_from_id(user_id)
        if msgs is None:
            return redirect('/')
        return render_template('messages.html', form=form, user=user, messages=msgs)


# обработчик удаления новости
@app.route('/del_new/<int:new_id>')
@login_required
def del_new(new_id):
    db_sess = db_session.create_session()
    new = db_sess.query(News).filter(News.id == new_id).first()
    if new:
        db_sess.delete(new)
        db_sess.commit()
    return redirect("/")


# страница с новостями
@app.route('/news')
@login_required
def news():
    db_sess = db_session.create_session()
    newss = []
    for i in FM.user_friends(current_user.id):
        _news = db_sess.query(News).filter(News.u_id == i).all()
        if _news:
            for new in _news:
                newss += [(new, db_sess.query(User).filter(User.id == i).first())]
    newss.sort(key=lambda x: -x[0].id)
    return render_template('news.html', news=newss)


# обработчик дизлайканья новости
@app.route('/dislike/<int:new_id>/<string:fr>')
@login_required
def dislike(new_id, fr):
    db_sess = db_session.create_session()
    new = db_sess.query(News).filter(News.id == new_id).first()
    if new:
        new.id = new_id
        new.dislikes += 1
        db_sess.merge(new)
        db_sess.commit()

    if fr == '0':
        return redirect("/")
    elif fr == '-1':
        return redirect('/news')
    else:
        return redirect(f'/user/{fr}')


# страница с лотереей лягушек
@app.route('/frog_lottery')
@login_required
def frog_lottery():
    db_sess = db_session.create_session()
    frogs = db_sess.query(Zhaba).filter(Zhaba.u_id == 0).all()
    return render_template('frogs.html', frogs=frogs)


# разблокировка жабы
@app.route('/open_frog/<int:pw>/<int:zh_id>')
@login_required
def open_frog(pw, zh_id):
    db_sess = db_session.create_session()
    frog = db_sess.query(Zhaba).filter(Zhaba.id == zh_id).first()
    if frog:
        if frog.pw == pw:
            frog.id = zh_id
            frog.u_id = current_user.id
            db_sess.merge(frog)
        else:
            db_sess.delete(frog)

        db_sess.commit()

    return redirect('/frog_lottery')


# отпустить жабу
@app.route('/release_frog/<int:zh_id>')
@login_required
def release_frog(zh_id):
    db_sess = db_session.create_session()
    frog = db_sess.query(Zhaba).filter(Zhaba.id == zh_id).first()
    if frog:
        idd = frog.u_id
        frog.id = zh_id
        frog.u_id = 0
        frog.pw = randint(0, 9)

        db_sess.merge(frog)
        db_sess.commit()

        return redirect(f'/user_zhabs/{idd}')
    return redirect('/')


# страница жаб пользователя
@app.route('/user_zhabs/<int:u_id>')
@login_required
def u_zhabs(u_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == u_id).first()
    return render_template('u_zh.html',
                           zhabs=ZhM.all_zh(u_id),
                           user=user
                           )


# обработчик выхода из профиля
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# ошибка
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': f'Not found'}), 404)


# АПИ всех пользователей
@app.route('/api/all_users')
def api_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()

    return jsonify(
        {
            'users': [
                item.to_dict(only=('name', 'about')) for item in users
            ]
        }
    )


# АПИ всех новостей
@app.route('/api/all_news')
def api_news():
    db_sess = db_session.create_session()
    users = db_sess.query(News).all()

    return jsonify(
        {
            'news': [
                item.to_dict(only=('text', 'dislikes')) for item in users
            ]
        }
    )


# АПИ всех жаб
@app.route('/api/all_zhabs')
def api_zhabs():
    db_sess = db_session.create_session()
    users = db_sess.query(Zhaba).all()

    return jsonify(
        {
            'zhabs': [
                item.to_dict(only=('name1', 'name2', 'name3')) for item in users
            ]
        }
    )


# АПИ добавления жабы
@app.route('/api/add_zhaba', methods=['POST'])
def add_zhaba():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name1', 'name2', 'name3', 'pw', 'u_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    frog = Zhaba(
        name1=request.json['name1'],
        name2=request.json['name2'],
        name3=request.json['name3'],
        pw=request.json['pw'],
        u_id=request.json['u_id'],
    )
    db_sess.add(frog)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# АПИ добавления новости
@app.route('/api/add_new', methods=['POST'])
def add_new():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['email', 'password', 'text']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == request.json['email']).first()
    if not user:
        return jsonify({'error': 'No user'})
    if not user.check_password(request.json['password']):
        return jsonify({'error': 'Bad password'})

    new = News(
        text=request.json['text'],
        u_id=user.id
    )
    db_sess.add(new)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# АПИ всех сообщений
@app.route('/api/send_mess', methods=['POST'])
def send_mess():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['email', 'password', 'text', 'email_to']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == request.json['email']).first()
    user2 = db_sess.query(User).filter(User.email == request.json['email_to']).first()
    if not (user and user2):
        return jsonify({'error': 'No user'})
    if not user.check_password(request.json['password']):
        return jsonify({'error': 'Bad password'})
    if not FM.is_friends(user.id, user2.id):
        return jsonify({'error': 'U must be friends'})

    mes = Messages(
        text=request.json['text'],
        u_id=user.id,
        b_id=FM.id_fr(user.id, user2.id)
    )
    db_sess.add(mes)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# запуск творения иисуса
def main():
    db_session.global_init("db/user.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
