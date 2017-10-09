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

    def test_bucket_list_route_returns_200_for_authenticated_users(self):
        """Test that bucketlist route returns response code 200"""
        with self.client:
            login_response = self.login()
            login_data = json.loads(login_response.data.decode("utf-8"))
            jwt_token = login_data.get("token")
            headers = {'Authorization': 'Bearer {0}'.format(jwt_token)}
            response = self.client.get("/bucketlists/", headers=headers)
            self.assert200(response)

    def test_bucket_list_route_raises_error_with_none_type_jwt(self):
        """Test that bucketlist route raises PermissionDenied error with None jwt token"""
        with self.assertRaises(PermissionDenied) as ctx:
            headers = {'Authorization': 'Bearer {0}'.format(None)}
            self.login()
            self.client.get("/bucketlists/", headers=headers)
            self.assertTrue("You need to pass your token as a header" in ctx)
            self.assertIsNotNone(ctx)

    def test_bucket_list_route_redirects_with_302_for_unauthenticated_users(self):
        response = self.client.get("/bucketlists/")
        self.assertEqual(response.status_code, 302)

    def test_bucket_list_route_with_incorrect_page_query_raises_error(self):
        """Test that bucketlist route with an incorrect page query raises error"""
        login_response = self.login()
        login_data = json.loads(login_response.data.decode("utf-8"))
        jwt_token = login_data.get("token")
        headers = {"Authorization": "Bearer {0}".format(jwt_token)}

        # response = self.client.get("/bucketlists/", headers=headers)

    def test_user_can_get_bucket_list_items(self):
        """Test that an authorized user can get their bucket list items"""


if __name__ == "__main__":
    unittest.main()
