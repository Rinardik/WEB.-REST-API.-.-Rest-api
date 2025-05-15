import unittest
import json
from flask import Flask
from flask_restful import Api
from data.db_session import global_init, create_session
from data.jobs import Job
from jobs_resource import JobsResource, JobsListResource

class JobsAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Инициализация приложения и API
        cls.app = Flask(__name__)
        cls.api = Api(cls.app)
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        
        # Инициализация базы данных (используем тестовую БД)
        global_init('sqlite:///:memory:')
        
        # Добавление тестовых данных
        db_sess = create_session()
        test_job = Job(
            job_title="Test Job",
            team_leader_id=1,
            work_size=10,
            collaborators="1,2,3",
            is_finished=False,
            category_id=1
        )
        db_sess.add(test_job)
        db_sess.commit()
        
        # Регистрация ресурсов
        cls.api.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')
        cls.api.add_resource(JobsListResource, '/api/v2/jobs')
        
        # Создание тестового клиента
        cls.client = cls.app.test_client()

    def test_1_get_existing_job(self):
        """Тест получения существующей работы"""
        response = self.client.get('/api/v2/jobs/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['job_title'], "Test Job")

    def test_2_get_nonexistent_job(self):
        """Тест получения несуществующей работы"""
        response = self.client.get('/api/v2/jobs/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('not found', data['message'].lower())

    def test_3_create_job_valid_data(self):
        """Тест создания работы с валидными данными"""
        new_job_data = {
            "job_title": "New Job",
            "team_leader_id": 2,
            "work_size": 20,
            "collaborators": "4,5,6",
            "is_finished": True,
            "category_id": 2
        }
        response = self.client.post(
            '/api/v2/jobs',
            data=json.dumps(new_job_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['job_title'], "New Job")

    def test_4_create_job_invalid_data(self):
        """Тест создания работы с невалидными данными"""
        invalid_job_data = {
            "team_leader_id": 2,
            "work_size": "twenty",  # Неверный тип
            "collaborators": "4,5,6",
            "is_finished": True,
            "category_id": 2
        }
        response = self.client.post(
            '/api/v2/jobs',
            data=json.dumps(invalid_job_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('cannot be blank', data['message'])

    def test_5_update_job_valid_data(self):
        """Тест обновления работы с валидными данными"""
        update_data = {
            "job_title": "Updated Job",
            "team_leader_id": 3,
            "work_size": 15,
            "collaborators": "7,8,9",
            "is_finished": False,
            "category_id": 3
        }
        response = self.client.put(
            '/api/v2/jobs/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['job_title'], "Updated Job")

    def test_6_update_job_invalid_data(self):
        """Тест обновления работы с невалидными данными"""
        invalid_data = {
            "job_title": "",
            "team_leader_id": 3,
            "work_size": 15,
            "collaborators": "7,8,9",
            "is_finished": False,
            "category_id": 3
        }
        response = self.client.put(
            '/api/v2/jobs/1',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_7_delete_existing_job(self):
        """Тест удаления существующей работы"""
        # Сначала создаем новую работу для удаления
        db_sess = create_session()
        test_job = Job(
            job_title="Job to delete",
            team_leader_id=1,
            work_size=5,
            collaborators="10",
            is_finished=True,
            category_id=1
        )
        db_sess.add(test_job)
        db_sess.commit()
        
        response = self.client.delete(f'/api/v2/jobs/{test_job.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data['message'].lower())

    def test_8_delete_nonexistent_job(self):
        """Тест удаления несуществующей работы"""
        response = self.client.delete('/api/v2/jobs/999')
        self.assertEqual(response.status_code, 404)

    def test_9_get_all_jobs(self):
        """Тест получения списка всех работ"""
        response = self.client.get('/api/v2/jobs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data['jobs'], list)
        self.assertGreater(len(data['jobs']), 0)

if __name__ == '__main__':
    unittest.main()