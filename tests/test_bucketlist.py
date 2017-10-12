import json
import unittest
from flask_api.exceptions import PermissionDenied, NotFound
from faker import Faker
from app.mod_bucketlist.exceptions import NullBucketListException, NullReferenceException
from app.mod_bucketlist.models import BucketListItem, BucketList
from tests import BaseTestCase


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

    def test_bucket_list_route_for_non_existent_query_returns_empty_list(self):
        """Test that bucketlist route returns no bucket list message"""
        data = {"q": "Buy Gold Watch", "page": 5, "limit": 20}
        response = self.client.get("/bucketlists/", headers=self.get_headers(),
                                   query_string=data)
        self.assertListEqual([], json.loads(response.data.decode("utf-8")).get("message"))

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

    def test_user_can_create_a_bucket_list(self):
        """Tests that a user can create a bucket list"""
        # setup
        jwt_token = self.get_jwt_token()
        headers = {"Authorization": "Bearer {0}".format(jwt_token)}
        data = {"name": "Eat, Pray, Love, Sh*t"}

        # post
        post_response = self.client.post("/bucketlists/", data=data, headers=headers)

        # assert
        self.assertIn("bucketlist", post_response.data.decode("utf-8"))
        self.assertEqual(post_response.status_code, 201)

    def test_user_can_search_bucketlists(self):
        """Tests users can search for an existing bucketlist """
        names = [
            "Become a pythonista",
            "Go out for a party",
            "Make a drone",
            "Make a comeback",
        ]
        for name in names:
            self.client.post('/bucketlists/', data={"name": name},
                             headers=self.get_headers())
        # search for a bucketlist starting with "Make"
        rv = self.client.get('/bucketlists/?q=Make', headers=self.get_headers())
        self.assert200(rv)

        results_data = json.loads(rv.data.decode("utf-8"))
        results_length = len(results_data['message'])
        self.assertEqual(results_length, 2)

    def test_pagination_limit_and_range(self):
        """Test bucketlist pagination"""
        # ENDPOINT: GET /bucketlist?limit=20
        faker = Faker()
        rv = self.client.post('/bucketlists/', data={'name': 'Make a drone'},
                              headers=self.get_headers())
        self.assertEqual(rv.status_code, 201)

        for i in range(0, 200):
            self.client.post('/bucketlists/',data={'name': faker.bs()},
                             headers=self.get_headers())
        rv = self.client.get('/bucketlists/?limit=20', headers=self.get_headers())
        rv_data = json.loads(rv.data.decode("utf-8"))
        rv_length = len(rv_data['message'])

        # Return 20 bucketlist items
        self.assertEqual(rv_length, 20)
        rvp = self.client.get('/bucketlists/?limit=1000', headers=self.get_headers())

        # Returns only the first 100 records
        self.assert200(rvp)

        # Return 100 bucketlist items for limit > 100
        rv_data = json.loads(rvp.data.decode("utf-8"))
        rv_length = len(rv_data['message'])

        # Return a maximum of 100 bucketlist items if limit > 100
        self.assertEqual(rv_length, 100)


class BucketListByIdTestCases(BaseTestCase):
    """Test cases for bucketlist route by id"""

    def test_raises_error_on_non_existent_bucketlist(self):
        """Test raises an error on a non-existent bucketlist item"""
        with self.assertRaises(NullBucketListException) as ctx:
            response = self.client.get("/bucketlists/4", headers=self.get_headers())
            self.assert404(response)
            self.assertTrue(NullBucketListException.detail, ctx.exception)
            self.assertTrue(NullBucketListException.status_code, 404)

    def test_user_can_delete_a_bucket_list_with_its_id(self):
        """Test that a user can delete their bucket list given its id"""

        # delete request
        response = self.client.delete("/bucketlists/1", headers=self.get_headers())

        # assert we get response of 200
        self.assert200(response)
        self.assertIn("Bucketlist was deleted successfully", response.data.decode("utf-8"))

        # check that the bucket list is no more
        with self.assertRaises(NullBucketListException) as ctx:
            new_response = self.client.get("/bucketlists/4", headers=self.get_headers())
            self.assert404(new_response)
            self.assertTrue(NullBucketListException.detail, ctx.exception)
            self.assertIn("No such bucketlist", new_response.data.decode("utf-8"))

    def test_user_can_put_a_bucketlist(self):
        """Test a user can edit a given bucket list item with its id"""
        # put request to edit a given bucket list
        response = self.client.put("/bucketlists/1", data={"name": "Eat! Eat a lot of food"},
                                   headers=self.get_headers(),
                                   )

        # assert the request was a success
        self.assertIn("Bucketlist edited successfully!", response.data.decode("utf-8"))
        self.assert200(response)

        # check that the same id 1, has a different bucket list item
        results = self.client.get("/bucketlists/1", headers=self.get_headers())
        self.assertIn("Eat! Eat a lot of food", results.data.decode("utf-8"))


class BucketListItemTestCases(BaseTestCase):
    """Tests for a single bucketlist item"""

    def test_user_can_get_their_bucketlist_items(self):
        """Test that a user can get their bucket list items"""
        response = self.client.get("/bucketlists/1/items", headers=self.get_headers())
        self.assertIn("User1 Bucketlist Item 0", response.data.decode("utf-8"))
        self.assertIn("User1 Bucketlist Item 1", response.data.decode("utf-8"))
        self.assertIn("User1 Bucketlist Item 2", response.data.decode("utf-8"))
        self.assert200(response)

    def test_user_can_create_a_bucket_list_item(self):
        """Test that a user can create a bucketlist item for a single bucketlist"""
        data = {"name": "Buy a car"}
        post_response = self.client.post("/bucketlists/1/items",
                                         headers=self.get_headers(), data=data)
        self.assertTrue(post_response.status_code, 201)
        self.assertIn("BucketList item added successfully.",
                      post_response.data.decode("utf-8"))
        self.assertIn(data.get("name"), post_response.data.decode("utf-8"))

        # check that the bucket list item exists in the db
        get_response = self.client.get("/bucketlists/1/items", headers=self.get_headers())
        self.assertIn(data.get("name"), get_response.data.decode("utf-8"))

    def test_user_can_retrieve_bucket_list_items(self):
        """Test user can retrieve bucketlist items by id"""
        get_response = self.client.get("/bucketlists/1/items/1",
                                       headers=self.get_headers())
        self.assert200(get_response)
        self.assertIn("User1 Bucketlist Item 0", get_response.data.decode("utf-8"))

    def test_user_can_edit_bucket_list_items(self):
        """Test that a user can edit bucketlist items by id"""
        data = {"name": "User1 Bucketlist Item 1", "done": True}
        put_response = self.client.put("/bucketlists/1/items/1",
                                       headers=self.get_headers(), data=data)
        self.assert200(put_response)
        self.assertIn("Successfully edited bucketlist item",
                      put_response.data.decode("utf-8"))

        # check that the bucketlist item was modified
        bucketlist_item = BucketListItem.query.get(1)
        self.assertTrue(bucketlist_item.done)

    def test_user_can_delete_a_bucketlist_item(self):
        """Test that a user can delete a bucketlist item by id"""
        delete_response = self.client.delete("/bucketlists/1/items/1",
                                             headers=self.get_headers())

        self.assert200(delete_response)
        self.assertIn("Bucketlist item was successfully deleted",
                      delete_response.data.decode("utf-8"))

        with self.assertRaises(NullReferenceException) as ctx:
            # try to fetch the resource
            get_response = self.client.get("/bucketlists/1/items/1",
                                           headers=self.get_headers())

            self.assertIn("No such Item", get_response.data.decode("utf-8"))

            # assert that the bucketlist item is not in db anymore
            bucketlist_item = BucketListItem.query.get(1)
            self.assertIsNone(bucketlist_item)
            self.assertIn(NullReferenceException.detail, ctx.exception)
            self.assert404(get_response)


if __name__ == "__main__":
    unittest.main()
