from flask import Flask, render_template, redirect, url_for, abort, request, Blueprint, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.jobs import Job
from forms.login import LoginForm
from forms.user import RegisterForm
from forms.job import JobForm
from data.departments import Department
from forms.department import DepartmentForm
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from data.categories import Category
import os
import requests
from flask import send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mars_explorer_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///db/blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

blueprint = Blueprint('jobs_api', __name__, url_prefix='/api')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    jobs_list = db_sess.query(Job).all()
    return render_template('index.html', jobs=jobs_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', message='Пароли не совпадают', form=form)

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', message='Такой пользователь уже существует', form=form)

        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.address = form.city_from.data
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect(url_for('login'))

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    db_sess = db_session.create_session()
    form.category_id.choices = [(c.id, f"{c.name} (level {c.hazard_level})") 
                              for c in db_sess.query(Category).all()]
    if form.validate_on_submit():
        job = Job(
            job_title=form.job_title.data,
            team_leader_id=form.team_leader_id.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
            category_id=form.category_id.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect(url_for('index'))
    else:
        print("Form errors:", form.errors)
    return render_template('add_job.html', title='Добавить работу', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/jobs/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    db_sess = db_session.create_session()

    job = db_sess.query(Job).get(job_id)
    if not job:
        abort(404)
    if job.team_leader_id != current_user.id and current_user.id != 1:
        abort(403)
    form = JobForm()
    form.category_id.choices = [
        (1, "Программирование (level 1)"),
        (2, "Дизайн (level 2)"),
        (3, "Маркетинг (level 1)"),
        (4, "Администрирование (level 3)"),
        (5, "Тестирование (level 2)")
    ]
    if form.validate_on_submit():
        job.job_title = form.job_title.data
        job.team_leader_id = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        job.category_id = form.category_id.data
        db_sess.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.job_title.data = job.job_title
        form.team_leader_id.data = job.team_leader_id
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished
        form.category_id.data = job.category_id
    return render_template('add_job.html', title='Редактировать работу', form=form)


@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()

    job = db_sess.query(Job).get(job_id)
    if not job:
        abort(404)
    if job.team_leader_id != current_user.id and current_user.id != 1:
        abort(403)
    db_sess.delete(job)
    db_sess.commit()
    return redirect(url_for('index'))


@app.route('/departments')
def departments_list():
    db_sess = db_session.create_session()
    departments_list = db_sess.query(Department).all()
    return render_template('departments.html', departments=departments_list)


@app.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = Department()
        department.title = form.title.data
        department.chief_id = int(form.chief_id.data)
        department.members = form.members.data
        department.email = form.email.data
        db_sess.add(department)
        db_sess.commit()
        return redirect(url_for('departments_list'))
    return render_template('edit_department.html', title='Добавить департамент', form=form)


@app.route('/departments/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    form = DepartmentForm()
    db_sess = db_session.create_session()
    department = db_sess.query(Department).get(department_id)

    if not department:
        abort(404)

    if department.chief_id != current_user.id and current_user.id != 1:
        abort(403)

    if form.validate_on_submit():
        department.title = form.title.data
        department.chief_id = int(form.chief_id.data)
        department.members = form.members.data
        department.email = form.email.data

        db_sess.commit()
        return redirect(url_for('departments_list'))

    elif request.method == 'GET':
        form.title.data = department.title
        form.chief_id.data = str(department.chief_id)
        form.members.data = department.members
        form.email.data = department.email

    return render_template('edit_department.html', title='Редактировать департамент', form=form)


@app.route('/departments/<int:department_id>/delete', methods=['POST'])
@login_required
def delete_department(department_id):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).get(department_id)

    if not department:
        abort(404)

    if department.chief_id != current_user.id and current_user.id != 1:
        abort(403)

    db_sess.delete(department)
    db_sess.commit()

    return redirect(url_for('departments_list'))


@app.route('/add_test_job')
def add_test_job():
    db_sess = db_session.create_session()
    job = Job()
    job.job_title = "Исследование грунта"
    job.team_leader_id = 1
    job.work_size = 10
    job.collaborators = "2,3"
    job.is_finished = False
    db_sess.add(job)
    db_sess.commit()
    return "Работа добавлена"


@blueprint.route('/jobs', methods=['GET'])
def get_jobs():
    db_sess = db_session.create_session()
    jobs_list = db_sess.query(Job).all()

    return jsonify({
        'jobs': [job.to_dict() for job in jobs_list]
    })


def abort_if_job_not_found(job_id):
    db_sess = db_session.create_session()
    job = db_sess.get(Job, job_id)
    if not job:
        abort(404, description=f"Работа с ID {job_id} не найдена")


@blueprint.route('/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    abort_if_job_not_found(job_id)
    db_sess = db_session.create_session()
    job = db_sess.get(Job, job_id)
    return jsonify({
        'job': job.to_dict()
    })


@blueprint.route('/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    required_fields = {
        'job_title': str,
        'team_leader_id': int,
        'work_size': int,
        'collaborators': str,
        'is_finished': bool,
        'hazard_category_id': int
    }

    for field, field_type in required_fields.items():
        if field not in request.json:
            return jsonify({'error': f'Missing field: {field}'}), 400
        if not isinstance(request.json[field], field_type):
            return jsonify({'error': f'Field {field} must be of type {field_type.__name__}'}), 400

    db_sess = db_session.create_session()

    job = Job(
        job_title=request.json['job_title'],
        team_leader_id=request.json['team_leader_id'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        is_finished=request.json['is_finished'],
        hazard_category_id=request.json['hazard_category_id']
    )

    db_sess.add(job)
    db_sess.commit()

    return jsonify({'id': job.id}), 201


@blueprint.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    abort_if_job_not_found(job_id)
    db_sess = db_session.create_session()
    job = db_sess.get(Job, job_id)
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'success': 'Работа успешно удалена'})



@blueprint.route('/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    abort_if_job_not_found(job_id)

    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    db_sess = db_session.create_session()
    job = db_sess.get(Job, job_id)

    update_fields = {
        'job_title': str,
        'team_leader_id': int,
        'work_size': int,
        'collaborators': str,
        'is_finished': bool,
        'hazard_category_id': int
    }

    for field, field_type in update_fields.items():
        if field in request.json:
            if isinstance(request.json[field], field_type):
                setattr(job, field, request.json[field])
            else:
                return jsonify({'error': f'Field {field} must be of type {field_type.__name__}'}), 400

    db_sess.commit()
    return jsonify({'success': 'Работа обновлена'})



blueprint_user = Blueprint('users_api', __name__, url_prefix='/api')


def abort_if_user_not_found(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if not user:
        abort(404, description=f"Пользователь с ID {user_id} не найден")


@blueprint_user.route('/users', methods=['GET'])
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    })


@blueprint_user.route('/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    abort_if_user_not_found(user_id)
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    return jsonify({
        'user': user.to_dict()
    })


@blueprint_user.route('/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    required_fields = {
        'surname': str,
        'name': str,
        'age': int,
        'position': str,
        'speciality': str,
        'address': str,
        'email': str,
        'hashed_password': str,
        'city_from': str
    }
    for field, field_type in required_fields.items():
        if field not in request.json:
            return jsonify({'error': f'Missing field: {field}'}), 400
        if not isinstance(request.json[field], field_type):
            return jsonify({'error': f'Field {field} must be of type {field_type.__name__}'}), 400

    db_sess = db_session.create_session()
    existing_user = db_sess.query(User).filter(User.email == request.json['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400

    user = User(
        surname=request.json['surname'],
        name=request.json['name'],
        age=request.json['age'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        email=request.json['email'],
        hashed_password=request.json['hashed_password'],
        city_from=request.json.get('city_from', '')
    )

    db_sess.add(user)
    db_sess.commit()

    return jsonify({'id': user.id}), 201


@blueprint_user.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    abort_if_user_not_found(user_id)

    if not request.json:
        return jsonify({'error': 'Empty request'}), 400

    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)

    allowed_fields = {
        'surname': str,
        'name': str,
        'age': int,
        'position': str,
        'speciality': str,
        'address': str,
        'email': str,
        'hashed_password': str
    }

    for field, field_type in allowed_fields.items():
        if field in request.json:
            if isinstance(request.json[field], field_type):
                setattr(user, field, request.json[field])
            else:
                return jsonify({'error': f'Field {field} must be of type {field_type.__name__}'}), 400

    db_sess.commit()
    return jsonify({'success': 'Пользователь обновлён'})


@blueprint_user.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    abort_if_user_not_found(user_id)
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'Пользователь удалён'})


@app.route('/users_show/<int:user_id>')
def users_show(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    
    print("User object:", user)
    if user:
        print("User city_from:", user.address)
    else:
        abort(404)
    
    def get_coordinates(city):
        if not city:
            print('City is not specified!' * 3)
            return None
            
        server_address1 = 'http://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        geocoder_request = f'{server_address1}apikey={api_key}&geocode={city}&format=json'
        
        try:
            response = requests.get(geocoder_request)
            response.raise_for_status()
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            return toponym["Point"]["pos"].split()
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    coordinates = get_coordinates(user.address)
    
    if not coordinates:
        abort(400, description="Could not get coordinates for the city")
    
    server_address2 = 'https://static-maps.yandex.ru/1.x?'
    map_params = {
        'll': ','.join(coordinates),
        'spn': '0.5,0.5',
        'l': 'map',
        'pt': ','.join(coordinates) + ',pm2rdm',
        'apikey': 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
    }
    
    response = requests.get(server_address2, params=map_params)
    if not response:
        abort(500)
    
    map_filename = f"map_{user_id}.png"
    with open(f"static/{map_filename}", "wb") as file:
        file.write(response.content)
        
    return render_template(
        'users_show.html',
        title=f"{user.surname} {user.name}",
        user=user,
        map_filename=map_filename
    )


@app.route('/cleanup_map/<filename>')
def cleanup_map(filename):
    try:
        os.remove(os.path.join('static', filename))
        return "Файл удален"
    except:
        return "Ошибка при удалении файла", 500
    

def add_default_categories():
    db_sess = db_session.create_session()
    if not db_sess.query(Category).first():
        categories = [
            Category(name="Research", hazard_level=1),
            Category(name="Terraforming", hazard_level=3),
            Category(name="Construction", hazard_level=2),
            Category(name="Life Support", hazard_level=2)
        ]
        db_sess.add_all(categories)
        db_sess.commit()


if __name__ == '__main__':
    db_path = "db/blogs.db"
    db_session.global_init(db_path)
    app.run(port=8080, host='127.0.0.1', debug=True)