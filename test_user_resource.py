import unittest
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/users"
TEST_USER = {
    "surname": "Иванов",
    "name": "Иван",
    "age": 30,
    "position": "инженер",
    "speciality": "разработка ПО",
    "address": "Москва",
    "email": "ivanov@example.com",
    "hashed_password": "password123"
}
UPDATED_USER = {
    "name": "Иван Иванович",
    "age": 31,
    "address": "Санкт-Петербург"
}


class TestUsersAPI(unittest.TestCase):

    def test_01_get_all_users(self):
        response = requests.get(BASE_URL)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)

    def test_02_get_user_valid_id(self):
        response = requests.get(f"{BASE_URL}/1")
        if response.status_code == 200:
            data = response.json()
            self.assertIn("user", data)
            self.assertIn("id", data["user"])
        else:
            print("Пользователь с ID=1 не найден")

    def test_03_get_user_invalid_id(self):
        response = requests.get(f"{BASE_URL}/999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_04_create_user_success(self):
        response = requests.post(BASE_URL, json=TEST_USER)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
        return response.json()['id']

    def test_05_create_user_missing_fields(self):
        incomplete_data = {
            "name": "Петр"
        }
        response = requests.post(BASE_URL, json=incomplete_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_06_create_user_wrong_types(self):
        wrong_data = TEST_USER.copy()
        wrong_data['age'] = 'тридцать'
        response = requests.post(BASE_URL, json=wrong_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Field age must be of type int", response.text)

    def test_07_create_user_duplicate_email(self):
        response = requests.post(BASE_URL, json=TEST_USER)
        self.assertEqual(response.status_code, 400)
        self.assertIn("User with this email already exists", response.text)

    def test_08_edit_user_success(self):
        user_id = 1
        response = requests.put(f"{BASE_URL}/{user_id}", json=UPDATED_USER)
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_09_edit_user_invalid_id(self):
        response = requests.put(f"{BASE_URL}/999999", json=UPDATED_USER)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_10_delete_user_success(self):
        user_id = 2
        response = requests.delete(f"{BASE_URL}/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_11_delete_user_invalid_id(self):
        response = requests.delete(f"{BASE_URL}/999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_12_invalid_method(self):
        response = requests.patch(BASE_URL)
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main(verbosity=2)