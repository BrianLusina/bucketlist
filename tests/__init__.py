import unittest
from datetime import datetime
from flask_testing import TestCase
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.mod_auth.models import UserAccount, UserProfile
from app.mod_bucketlist.models import BucketList, BucketListItem


class ContextTestCase(TestCase):
    render_templates = True

    def create_app(self):
        app = create_app("testing")
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return app

    def _pre_setup(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def __call__(self, result=None):
        try:
            self._pre_setup()
            super(ContextTestCase, self).__call__(result)
        finally:
            self._post_teardown()

    def _post_teardown(self):
        if getattr(self, '_ctx', None) and self._ctx is not None:
            self._ctx.pop()
            del self._ctx


class BaseTestCase(ContextTestCase):
    """
    Base test case for application
    """

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = db

        db.create_all()

        self.create_user_accounts()
        self.create_bucket_lists()

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @staticmethod
    def create_user_accounts():
        """
        Creates new users for testing follow feature
        :return: 2 new unique users to test follow and unfollow feature
        """

        user1_profile = UserProfile(first_name="user1", last_name="user1Lastname",
                                    email="user1@example.com")

        user2_profile = UserProfile(first_name="user2", last_name="user2LastName",
                                    email="user2@example.com")
        db.session.add(user1_profile)
        db.session.add(user2_profile)
        db.session.commit()

        user1_account = UserAccount(username="user1", email="user1@example.com",
                                    password="user1_password",
                                    registered_on=datetime.now(),
                                    user_profile_id=user1_profile.id)

        user2_account = UserAccount(username="user2", email="user2@example.com",
                                    password="user2_password", registered_on=datetime.now(),
                                    user_profile_id=user2_profile.id)

        try:
            db.session.add(user2_account)
            db.session.add(user1_account)
            db.session.commit()
        except IntegrityError as ie:
            print("Integrity Error: ", ie)
            db.session.rollback()

        return user1_account, user2_account

    @staticmethod
    def create_bucket_lists(self):
        """Create bucket lists for each user account"""
        user1, user2 = self.create_user_accounts()

        bucket_list1 = BucketList(created_by=user1.id, name="User1 Bucketlist")
        bucket_list2 = BucketList(created_by=user2.id, name="User2 Bucketlist")

        db.session.add(bucket_list1)
        db.session.add(bucket_list2)
        db.session.commit()

        for n in range(5):
            bucket_list_items_1 = BucketListItem(bucketlist_id=bucket_list1.id,
                                                 name="User1 Bucketlist Item {}".format(n))
            db.session.add(bucket_list_items_1)

            bucket_list_items_2 = BucketListItem(bucketlist_id=bucket_list2.id,
                                                 name="User2 Bucketlist item {}".format(n))
            db.session.add(bucket_list_items_2)
        db.session.commit()

    def login(self):
        """
        Login in the user to the testing app
        :return: The authenticated user for the test app
        """
        return self.client.post(
            "/auth/login/", data=dict(email='user1@example.com', username="user1",
                                      password='user1_password'),
            follow_redirects=True
        )


if __name__ == "__main__":
    unittest.main()
