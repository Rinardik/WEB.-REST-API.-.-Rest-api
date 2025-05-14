import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/jobs"
GET_ALL_URL = BASE_URL
DELETE_URL_TEMPLATE = f"{BASE_URL}/{{job_id}}"

print("Тест 1: Удаление существующей работы")
job_id_to_delete = 5

response = requests.delete(f"{DELETE_URL_TEMPLATE.format(job_id=job_id_to_delete)}")
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 200, "Ошибка: ожидался статус 200"
assert response.json().get('success') == 'Работа успешно удалена', "Ошибка: сообщение об удалении некорректно"


print("\nТест 2: Удаление несуществующей работы")
nonexistent_job_id = 99999

response = requests.delete(f"{DELETE_URL_TEMPLATE.format(job_id=nonexistent_job_id)}")
print("Код ответа:", response.status_code)
print("Ответ сервера:", response.json())

assert response.status_code == 404, "Ошибка: ожидался статус 404"
assert 'Job not found' in response.json().get('message', ''), "Ошибка: ожидалось сообщение о ненайденной работе"


print("\nТест 3: Неверный тип ID — строка вместо числа")
invalid_id = "abc"

response = requests.delete(f"{DELETE_URL_TEMPLATE.format(job_id=invalid_id)}")
print("Код ответа:", response.status_code)

assert response.status_code == 404 or response.status_code == 400, "Ошибка: ожидался статус 404 или 400"
print("Получен ожидаемый код ошибки")


print("\nТест 4: Проверка, что работа удалена")
response = requests.get(GET_ALL_URL)
print("Код ответа:", response.status_code)

jobs = response.json().get('jobs', [])
job_exists = any(job['id'] == job_id_to_delete for job in jobs)

if job_exists:
    print("Ошибка: Работа всё ещё существует после удаления")
else:
    print("Успех: Работа с ID", job_id_to_delete, "удалена")

assert not job_exists, f"Ошибка: Работа с ID {job_id_to_delete} не удалена из базы данных"