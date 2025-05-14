import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/jobs"

print("Тест 1: Корректный POST-запрос")
correct_job = {
    "job_title": "Исследование грунта",
    "team_leader_id": 1,
    "work_size": 10,
    "collaborators": "2,3",
    "is_finished": False,
    "hazard_category_id": 2
}

response = requests.post(BASE_URL, json=correct_job)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 201, "Ошибка: ожидался статус 201"
job_id = response.json().get('id')
print("Работа успешно добавлена с ID =", job_id)


print("\nТест 2: Неверный тип данных — work_size не число")
invalid_type_job = correct_job.copy()
invalid_type_job['work_size'] = "десять"

response = requests.post(BASE_URL, json=invalid_type_job)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 400, "Ошибка: ожидался статус 400"
assert 'Field work_size must be of type int' in response.json()['error']


print("\nТест 3: Отсутствует обязательное поле — job_title")
missing_field_job = correct_job.copy()
missing_field_job.pop('job_title')
response = requests.post(BASE_URL, json=missing_field_job)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 400, "Ошибка: ожидался статус 400"
assert 'Missing field: job_title' in response.json()['error']


print("\nТест 4: Пустой запрос")
empty_request = {}

response = requests.post(BASE_URL, json=empty_request)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 400, "Ошибка: ожидался статус 400"
assert 'Empty request' in response.json()['error']


print("\nТест 5: Проверка, что работа добавилась через GET /api/jobs")
response = requests.get(BASE_URL)
print("Код ответа:", response.status_code)
print("Список всех работ:")
jobs = response.json()['jobs']
for job in jobs:
    print(json.dumps(job, indent=2))

job_exists = any(job['id'] == job_id for job in jobs)
assert job_exists, f"Ошибка: Работа с ID {job_id} не найдена в списке после добавления"
print("Работа с ID", job_id, "успешно найдена в общем списке")