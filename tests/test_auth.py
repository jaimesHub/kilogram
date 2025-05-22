import unittest
from app import create_app
from random import randint

class AuthApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        random_id = randint(1, 10000)
        self.user_info = {
            "username": "testuser" + str(random_id),
            "password": "testpassword",
            "fullname": "Test User" + str(random_id),
            "email": "user" + str(random_id) + "@sydexa.com",
        }
        
    def tearDown(self):
        pass

    def test_authentication_workflow(self):
        # Step 1: Register
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": self.user_info["username"],
                "password": self.user_info["password"],
                "fullname": self.user_info["fullname"],
                "email": self.user_info["email"],
            },
        )
        self.assertEqual(response.status_code, 201)

        # Step 2: Login
        response = self.client.post(
            "/api/auth/login",
            json={
                "username": self.user_info["username"],
                "password": self.user_info["password"],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json["data"])

        # Step 3: Get profile
        token = response.json["data"]["access_token"]
        response = self.client.get(
            "/api/users/profile", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.json["data"])
        self.assertEqual(response.json["data"]["username"], self.user_info["username"])
        

if __name__ == "__main__":
    unittest.main()