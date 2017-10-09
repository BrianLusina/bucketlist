from tests import BaseTestCase
from flask_api.exceptions import NotFound
from flask_login import current_user


class BucketListTestCase(BaseTestCase):
    """
    Bucket list test cases
    """

    def test_bucket_list_route_returns_200_for_authenticated_users(self):
        """Test that bucketlist route returns response code 200"""
        self.login()
        response = self.client.get("/bucketlists/")
        self.assert200(response)

    def test_bucket_list_route_redirects_with_302_for_unauthenticated_users(self):
        response = self.client.get("/bucketlists/")
        self.assertEqual(response.status_code, 302)

    def test_bucket_list_route_with_incorrect_page_query_raises_error(self):
        """Test that bucketlist route with an incorrect page query raises error"""
        login_response = self.login()
        response = self.client.get("/bucketlists/")

    def test_user_can_get_bucket_list_items(self):
        """Test that an authorized user can get their bucket list items"""
