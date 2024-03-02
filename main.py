from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.db_session import create_session, global_init
from data.users import User
from data.jobs import Jobs
from data.news import News
from data.forms.registerform import RegisterForm
from data.forms.loginform import LoginForm
from data.forms.newsform import NewsForm
from data.forms.jobform import JobForm
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)


def create_people(db_sess):
    data = [{'surname': 'Scott', 'name': 'Ridley', 'age': 21, 'position': 'captain', 'speciality': 'research engineer',
             'address': 'module_1', 'email': 'scott_chief@mars.org'},
            {'surname': 'Scott1', 'name': 'Ridley1', 'age': 20, 'position': 'no_captain', 'speciality': 'cool engineer',
             'address': 'module_2', 'email': 'scott1_chief@mars.org'},
            {'surname': 'Scott2', 'name': 'Ridley2', 'age': 19, 'position': 'no_captain', 'speciality': 'cool engineer',
             'address': 'module_2', 'email': 'scott2_chief@mars.org'},
            {'surname': 'Scott3', 'name': 'Ridley3', 'age': 18, 'position': 'no_captain', 'speciality': 'cool engineer',
             'address': 'module_2', 'email': 'scott3_chief@mars.org'}]

    for i in data:
        user = User()
        user.surname = i['surname']
        user.name = i['name']
        user.age = i['age']
        user.position = i['position']
        user.speciality = i['speciality']
        user.address = i['address']
        user.email = i['email']

        db_sess.add(user)

    db_sess.commit()


def create_job(db_sess):
    job = Jobs()
    job.team_leader = 1
    job.job = 'deployment of residential modules 1 and 2'
    job.work_size = 15
    job.collaborators = '2, 3'
    job.start_date = datetime.datetime.now()
    job.is_finished = False

    db_sess.add(job)
    db_sess.commit()


def create_news(db_sess):
    news = News(title="Первая новость", content="Привет блог!",
                user_id=1, is_private=False)
    db_sess.add(news)

    user = db_sess.query(User).filter(User.id == 1).first()
    news = News(title="Вторая новость", content="Уже вторая запись!",
                user=user, is_private=False)
    db_sess.add(news)

    user = db_sess.query(User).filter(User.id == 1).first()
    news = News(title="Личная запись", content="Эта запись личная",
                is_private=True)
    user.news.append(news)

    db_sess.commit()


def main():
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/table')
def table():
    jobs_and_leaders = [(job, db_sess.query(User).filter(User.id == int(job.team_leader)).first())
                        for job in db_sess.query(Jobs).all()]
    return render_template('table.html', jobs_and_leaders=jobs_and_leaders)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.surname = request.form['surname']
        user.name = request.form['name']
        user.age = request.form['age']
        user.position = request.form['position']
        user.speciality = request.form['speciality']
        user.address = request.form['address']
        user.email = request.form['email']
        user.set_password(request.form['password'])
        user.modified_date = datetime.datetime.now()

        db_sess.add(user)
        db_sess.commit()

        return redirect('/index')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/job',  methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Jobs()
        job.title = form.title.data
        job.team_leader = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data

        db_sess.add(job)
        db_sess.commit()
        return redirect('/table')
    return render_template('job.html', title='Добавление работы',
                           form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route("/")
@app.route('/index')
def index():
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


if __name__ == '__main__':
    global_init('db/blogs.db')
    db_sess = create_session()
    main()
