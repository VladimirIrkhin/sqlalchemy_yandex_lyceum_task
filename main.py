from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from data.db_session import create_session, global_init
from data.users import User
from data.jobs import Jobs
from data.news import News
from data.forms.registerform import RegisterForm
from data.forms.loginform import LoginForm
from data.forms.newsform import NewsForm
from data.forms.jobform import JobForm
from data import news_resources, user_resources, job_resources
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
api = Api(app)
api.add_resource(news_resources.NewsListResource, '/api/v2/news')
api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')
api.add_resource(user_resources.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(user_resources.UserListResource, '/api/v2/users')
api.add_resource(job_resources.JobResource, '/api/v2/jobs/<int:job_id>')
api.add_resource(job_resources.JobListResource, '/api/v2/jobs')

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    global_init('db/blogs.db')
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route('/table')
def table():
    db_sess = create_session()
    jobs_and_leaders = [(job, db_sess.query(User).filter(User.id == int(job.team_leader)).first())
                        for job in db_sess.query(Jobs).all()]
    return render_template('table.html', jobs_and_leaders=jobs_and_leaders)


@app.route('/register', methods=['GET', 'POST'])
def register():
    db_sess = create_session()
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
    db_sess = create_session()
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
    db_sess = create_session()
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
    return render_template('news.html', title='Добавление новости', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    db_sess = create_session()
    form = NewsForm()
    if request.method == "GET":
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = create_session()
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
    db_sess = create_session()
    form = JobForm()
    if form.validate_on_submit():
        job = Jobs()
        job.job = form.title.data
        job.team_leader = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data

        db_sess.add(job)
        db_sess.commit()
        return redirect('/table')
    return render_template('job.html', title='Добавление работы',
                           form=form)


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    db_sess = create_session()
    form = JobForm()
    if request.method == "GET":
        job = db_sess.query(Jobs).filter(Jobs.id == id).first()   #

        print(job.team_leader == current_user.id)

        if job and (job.team_leader == current_user.id or current_user.id == 1):
            form.title.data = job.job
            form.team_leader_id.data = job.team_leader
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        job = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if job and (job.team_leader == current_user.id or current_user.id == 1):
            job.job = form.title.data
            job.team_leader = form.team_leader_id.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('job.html', title='Редактирование работы', form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    db_sess = create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if job and (job.team_leader == current_user.id or current_user.id == 1):
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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


@app.route('/index')
def index():
    db_sess = create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


if __name__ == '__main__':
    main()
