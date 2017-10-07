from tests import BaseTestCase
import app.mod_auth as auth
from app.mod_auth.exceptions import UserAlreadyExists
import json
import unittest


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
    """ Tests correct user authentication """

    @unittest.skip
    def test_registration(self):
        """Tests for correct user registration """
        user = {'username': 'user1', 'password': 'password'}
        req = self.client().get('/auth/register')
        self.assertEqual(req.status_code, 200)
        req = self.client().post('/auth/register', data=user)
        self.assertEqual(req.status_code, 201)
        self.assertIn('registered successfully', req.data)
        # test for empty registration: respond with bad request
        rv = self.client().post('/auth/register')
        self.assertEqual(rv.status_code, 400)

    @unittest.skip
    def test_user_already_exists(self):
        """Tests for the already existing user """
        user = {'username': 'Adelle', 'password': 'Hello'}
        req = self.client().get('/auth/register')
        req = self.client().post('/auth/register', data=user)
        self.assertEqual(req.status_code, 201)
        another_user = {'username': 'Adelle', 'password': 'Hello'}
        another_req = self.client().get('/auth/register')
        req = self.client().post('/auth/register', data=another_user)
        self.assertNotEqual(another_req.status_code, 201)

    # ENDPOINT: POST '/auth/login'
    @unittest.skip
    def test_logging_in(self):
        """Tests correct user login """
        req = self.client().post('/auth/login', data=self.user)
        self.assertEqual(req.status_code, 200)
        self.assertIn(auth.SERVICE_MESSAGES['login'], req.data)
        rv = self.client().get('/auth/login')
        self.assertEqual(rv.status_code, 202)
        # test for invalid credentials: respond with unauthorized
        wrong_req = self.client().post(
            '/auth/login',
            data={'username': 'its-me', 'password': 'i have no idea'})
        self.assertEqual(wrong_req.status_code, 401)

    # ENDPOINT: GET '/auth/logout'
    @unittest.skip
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
