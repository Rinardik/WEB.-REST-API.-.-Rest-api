from flask import abort
from flask_restful import Resource, reqparse
from data import db_session
from data.users import User


user_parser = reqparse.RequestParser()
user_parser.add_argument('surname', type=str, help='Фамилия пользователя')
user_parser.add_argument('name', type=str, required=True, help='Имя пользователя')
user_parser.add_argument('age', type=int, help='Возраст пользователя')
user_parser.add_argument('position', type=str, help='Должность')
user_parser.add_argument('speciality', type=str, help='Профессия')
user_parser.add_argument('address', type=str, help='Адрес')
user_parser.add_argument('email', type=str, required=True, help='Email пользователя')
user_parser.add_argument('hashed_password', type=str, help='Пароль')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return {
            'users': [user.to_dict(only=('id', 'surname', 'name', 'age', 'position',
                                        'speciality', 'address', 'email'))]
        }

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return {'success': 'OK'}

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(user_id)

        if args['surname']:
            user.surname = args['surname']
        if args['name']:
            user.name = args['name']
        if args['age']:
            user.age = args['age']
        if args['position']:
            user.position = args['position']
        if args['speciality']:
            user.speciality = args['speciality']
        if args['address']:
            user.address = args['address']
        if args['email']:
            user.email = args['email']
        if args['hashed_password']:
            user.set_password(args['hashed_password'])

        session.commit()
        return {'success': 'OK'}


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return {
            'users': [
                item.to_dict(only=('id', 'surname', 'name', 'age', 'position',
                                   'speciality', 'address', 'email'))
                for item in users
            ]
        }

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email']
        )
        user.set_password(args['hashed_password'])
        session.add(user)
        session.commit()
        return {'id': user.id}, 201