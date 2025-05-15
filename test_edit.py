import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/jobs"
GET_ALL_URL = BASE_URL
EDIT_URL_TEMPLATE = f"{BASE_URL}/{{job_id}}"

print("Тест 1: Корректное редактирование работы")
job_id_to_edit = 1

edit_data = {
    "job_title": "Обновлённая работа",
    "work_size": 15,
    "is_finished": True
}

response = requests.put(f"{EDIT_URL_TEMPLATE.format(job_id=job_id_to_edit)}", json=edit_data)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 200, "Ошибка: ожидался статус 200"
assert response.json().get('success') == 'Работа обновлена', "Ошибка: сообщение о редактировании некорректно"


print("\nТест 2: Редактирование несуществующей работы")
nonexistent_job_id = 99999

response = requests.put(f"{EDIT_URL_TEMPLATE.format(job_id=nonexistent_job_id)}", json=edit_data)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 404, "Ошибка: ожидался статус 404"
assert 'Job not found' in response.json().get('message', ''), "Ошибка: ожидалось сообщение о ненайденной работе"


print("\nТест 3: Неверный тип данных — work_size передан как строка")
invalid_type_data = edit_data.copy()
invalid_type_data['work_size'] = "пятнадцать"

response = requests.put(f"{EDIT_URL_TEMPLATE.format(job_id=job_id_to_edit)}", json=invalid_type_data)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 400, "Ошибка: ожидался статус 400"
assert 'Field work_size must be of type int' in response.json()['error'], "Ошибка: неверное сообщение об ошибке"


print("\nТест 4: Пустой запрос на редактирование")
empty_request = {}

response = requests.put(f"{EDIT_URL_TEMPLATE.format(job_id=job_id_to_edit)}", json=empty_request)
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 400, "Ошибка: ожидался статус 400"
assert 'Empty request' in response.json()['error'], "Ошибка: ожидалось сообщение о пустом запросе"


print("\nТест 5: Проверка, что работа изменена")
response = requests.get(GET_ALL_URL)
print("Код ответа:", response.status_code)

jobs = response.json().get('jobs', [])
edited_job = next((job for job in jobs if job['id'] == job_id_to_edit), None)

if edited_job:
    print("Данные работы после редактирования:")
    print(json.dumps(edited_job, indent=2))
    assert edited_job['job_title'] == edit_data['job_title'], "Ошибка: job_title не обновился"
    assert edited_job['work_size'] == edit_data['work_size'], "Ошибка: work_size не обновился"
    assert edited_job['is_finished'] == edit_data['is_finished'], "Ошибка: is_finished не обновился"
    print("Успех: Данные работы корректно обновлены")
else:
    print("Ошибка: Работа с ID", job_id_to_edit, "не найдена в списке после редактирования")
    assert False, "Работа не найдена после редактирования"