import json
import unittest

import app.mod_auth as auth
from app.mod_auth.exceptions import UserAlreadyExists, CredentialsRequired, AuthenticationFailed
from tests import BaseTestCase


class RegistrationTestCases(BaseTestCase):
    """Registration test cases"""

    def test_registration_returns_200_on_get_request(self):
        """Test registration page returns response of 200 for GET request"""
        response = self.client.get('auth/register/', follow_redirects=True)
        self.assert200(response)

    def test_registration_returns_200_on_post_request(self):
        """Test POST request to registration route returns 200"""
        response = self.client.post("auth/register/", follow_redirects=True)
        self.assert200(response)

    def test_registration_returns_201_when_user_data_is_posted(self):
        """Test POST request with data to registration returns 201 response"""
        user = {'username': 'user3', 'password': 'user3_password', "email": "user3_email"}
        req = self.client.post('/auth/register/', data=user)
        self.assertEqual(req.status_code, 201)

    def test_registration_raises_exception_when_user_exists(self):
        """Test registration route raises Exception when user already exists"""
        user = {'username': 'user2', 'password': 'user2_password', "email": "user2_email"}
        with self.assertRaises(UserAlreadyExists) as context:
            self.client.post('/auth/register/', data=user)
            self.assertTrue(UserAlreadyExists.detail in context.exception)


class LoginTestCases(BaseTestCase):
    """ Tests correct user login"""

    def test_correct_logging_in_returns_200(self):
        """Test login route returns 200"""
        response = self.login()
        self.assert200(response)

    def test_get_request_raises_credentials_required_error(self):
        """Test GET request to login without credentials raises error"""
        with self.assertRaises(CredentialsRequired) as context:
            self.client.get("/auth/login/")
            self.assertTrue(CredentialsRequired.detail in context.exception)

    def test_get_request_with_correct_credentials_returns_response(self):
        """Test GET request with correct credentials returns correct response"""
        response = self.login()
        self.assertIn(b'You have logged in successfully', response.data)

    def test_incorrect_logging_in_returns_401(self):
        """Tests incorrect user login will raise error"""
        wrong_req = self.client.post('/auth/login/', data=dict(username="itsme",
                                                               email="noclue@example.com",
                                                               password="i have no idea"))
        self.assert401(wrong_req)

    def test_incorrect_credentials_raises_error(self):
        """Tests incorrect user credentials raises error"""
        with self.assertRaises(AuthenticationFailed) as context:
            self.client.post('/auth/login/', data=dict(username="user1",
                                                       email="user1@example.com",
                                                       password="i have no idea"))
            self.assertEqual(AuthenticationFailed.detail, context.exception)

    def test_logging_out(self):
        """Test user correctly logging out"""
        get_res = self.client().post('/auth/login', data=self.user)
        get_res_json = json.loads(get_res.data)
        jwtoken = get_res_json.get('token')
        headers = {'Authorization': 'Bearer {0}'.format(jwtoken)}
        logout_req = self.client().get('/auth/logout', headers=headers)
        self.assertIn(auth.SERVICE_MESSAGES['logout'], logout_req.data)

    @unittest.skip
    def test_correct_token_generation(self):
        """Tests correct token generation"""
        rv = self.client().post(
            '/auth/login',
            data={'username': 'its-me', 'password': 'i have no idea'})
        res_json = json.loads(rv.data)
        jwtoken = res_json.get('token')
        self.assertIsNone(jwtoken)


if __name__ == "__main__":
    unittest.main()
