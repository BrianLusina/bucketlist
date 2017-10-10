from tests import BaseTestCase
from flask_api.exceptions import NotFound
from flask_login import current_user
import unittest
import json
from flask_api.exceptions import AuthenticationFailed, PermissionDenied, NotFound


class BucketListTestCase(BaseTestCase):
    """
    Bucket list test cases
    """

    def test_bucket_list_route_rasies_error_when_accessed_without_token(self):
        """Test that bucketlist route raises error without header token"""
        self.login()
        with self.assertRaises(PermissionDenied) as ctx:
            self.client.get("/bucketlists/")
            self.assertTrue(PermissionDenied.detail in ctx.exception)
            self.assertTrue("You need to pass your token as a header" in ctx)
            self.assertIsNotNone(ctx)

    def test_bucket_list_route_returns_200_for_authenticated_users(self):
        """Test that bucketlist route returns response code 200 for authenticated users"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
        data = {"q": "User1 Bucketlist Item 1", "page": 5}
        response = self.client.get("/bucketlists/", headers=headers, query_string=data)
        self.assert200(response)

    def test_bucket_list_route_raises_error_for_invalid_page_requests(self):
        """Test that bucketlist route raises error for invalid page requests arguments"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
        data = {"q": "Buy Gold Watch", "page": "my number"}

        with self.assertRaises(ValueError) as ctx:
            self.client.get("/bucketlists/", headers=headers, query_string=data)
            self.assertTrue(ValueError in ctx)
            self.assertTrue("Please specify an integer for the page request argument" in ctx)
            self.assertIsNotNone(ctx)

    def test_bucket_list_route_raises_Not_Found_error_for_negative_page_requests(self):
        """Test that bucketlist route raises error for invalid page requests arguments"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
        data = {"q": "Buy Gold Watch", "page": -5}

        with self.assertRaises(NotFound) as ctx:
            self.client.get("/bucketlists/", headers=headers, query_string=data)
            self.assertTrue(NotFound.detail in ctx)
            self.assertTrue("Please specify a valid page" in ctx)
            self.assertIsNotNone(ctx)

    def test_bucket_list_route_raises_error_for_invalid_limit_requests(self):
        """Test that bucketlist route raises error for invalid limit requests arguments"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
        data = {"q": "Buy Gold Watch", "page": 5, "limit": "some limit"}

        with self.assertRaises(ValueError) as ctx:
            self.client.get("/bucketlists/", headers=headers, query_string=data)
            self.assertTrue(ValueError in ctx)
            self.assertTrue("Please specify an integer for the limit request argument" in ctx)
            self.assertIsNotNone(ctx)

    def test_bucket_list_route_raises_not_found_error_for_empty_buckets(self):
        """Test that bucketlist route returns no bucket list message"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
        data = {"q": "Buy Gold Watch", "page": 5, "limit": 20}

        response = self.client.get("/bucketlists/", headers=headers, query_string=data)
        self.assertTrue("User has no bucket list" in response.data.decode("utf-8"))

    def test_bucket_list_route_redirects_with_302_for_unauthenticated_users(self):
        """Test that bucketlist route redirects to login page with status code 302"""
        response = self.client.get("/bucketlists/")
        self.assertEqual(response.status_code, 302)

    def test_user_can_get_bucket_list_items(self):
        """Test that an authorized user can get their bucket list items"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
        data = {"name": "Swallow a python"}

        # post new data
        self.client.post('/bucketlists/', data=data, headers=headers)

        # fetch the data
        response = self.client.get('/bucketlists/', headers=headers)

        # assert that the data is available
        self.assertIn('Swallow a python', response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
