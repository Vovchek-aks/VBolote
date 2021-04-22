from flask import Flask, redirect, render_template, request, abort, make_response, jsonify
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
import datetime as dt
from forms.login import LoginForm
from forms.message import MessageForm
from forms.register import RegisterForm
from forms.edit_user import EditUserForm
from forms.make_news import NewsForm
from data.users import User
from data.friends import Friends
from data.messages import Messages
from data.news import News
from data.zhabs import Zhaba
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class FM:
    @staticmethod
    def is_friends(id1, id2):
        db_sess = db_session.create_session()
        return (id2,) in db_sess.query(Friends.u_id2).filter(Friends.u_id1 == id1).all() or \
               (id1,) in db_sess.query(Friends.u_id2).filter(Friends.u_id1 == id2).all()

    @staticmethod
    def user_friends(u_id):
        db_sess = db_session.create_session()
        return list(map(lambda x: x[0], db_sess.query(Friends.u_id2).filter(Friends.u_id1 == u_id).all() + \
                        db_sess.query(Friends.u_id1).filter(Friends.u_id2 == u_id).all()))

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


class MM:
    @staticmethod
    def get_ms_from_id(user_id):
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


class ZhM:
    @staticmethod
    def all_zh(u_id):
        db_sess = db_session.create_session()
        return db_sess.query(Zhaba).filter(Zhaba.u_id == u_id).all()


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
                               zh_c=len(ZhM.all_zh(user_id))
                               )
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
    db_sess = db_session.create_session()
    fr = Friends(
        u_id1=current_user.id,
        u_id2=user_id
    )
    db_sess.add(fr)
    db_sess.commit()
    return redirect(f"/user/{user_id}")


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


@app.route('/all_users')
@login_required
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('all_users.html', users=users)


@app.route('/choose_ava')
@login_required
def choose_ava():
    return render_template('choose_ava.html')


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


@app.route('/friends/<int:user_id>')
@login_required
def friends(user_id):
    db_sess = db_session.create_session()
    fr = FM.user_friends(user_id)
    users = []
    for i in fr:
        users += db_sess.query(User).filter(User.id == i).all()
    return render_template('friends.html', users=users)


@app.route('/suicide')
@login_required
def suicide():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


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


@app.route('/del_new/<int:new_id>')
@login_required
def del_new(new_id):
    db_sess = db_session.create_session()
    new = db_sess.query(News).filter(News.id == new_id).first()
    if new:
        db_sess.delete(new)
        db_sess.commit()
    return redirect("/")


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


@app.route('/frog_lottery')
@login_required
def frog_lottery():
    db_sess = db_session.create_session()
    frogs = db_sess.query(Zhaba).filter(Zhaba.u_id == 0).all()
    return render_template('frogs.html', frogs=frogs)


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


@app.route('/user_zhabs/<int:u_id>')
@login_required
def u_zhabs(u_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == u_id).first()
    return render_template('u_zh.html',
                           zhabs=ZhM.all_zh(u_id),
                           user=user
                           )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': f'Not found'}), 404)


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
    if not user.check_password(request.json['pw']):
        return jsonify({'error': 'Bad password'})

    new = News(
        text=request.json['text'],
        u_id=user.id
    )
    db_sess.add(new)
    db_sess.commit()
    return jsonify({'success': 'OK'})


def main():
    db_session.global_init("db/user.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
