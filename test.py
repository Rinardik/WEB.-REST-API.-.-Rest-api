import requests

BASE_URL = "http://127.0.0.1:8080/api/jobs"


def test_get_all_jobs():
    response = requests.get(BASE_URL)
    print("\nТест: Получение всех работ")
    print("Статус код:", response.status_code)
    if response.status_code == 200:
        print("Ответ JSON:", response.json())
    else:
        print("Ошибка:", response.text)


def test_get_one_job(job_id):
    url = f"{BASE_URL}/{job_id}"
    print(f"\nТест: Получение работы с ID={job_id}")
    response = requests.get(url)
    print("Статус код:", response.status_code)
    if response.status_code == 200:
        print("Ответ JSON:", response.json())
    else:
        print("Ошибка:", response.text)


if __name__ == "__main__":
    test_get_all_jobs()
    test_get_one_job(1)
    test_get_one_job(999)
    test_get_one_job("abc")