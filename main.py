from flask import Flask, render_template, redirect, request
from data.db_session import create_session, global_init
from data.users import User
from data.jobs import Jobs
from data.registerform import RegisterForm
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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


def main():
    app.run(port=8080, host='127.0.0.1')


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


@app.route('/index')
def index():
    return render_template('base.html')


if __name__ == '__main__':
    global_init('db/blogs.db')
    db_sess = create_session()
    main()
