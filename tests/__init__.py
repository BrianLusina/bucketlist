import unittest
from app import create_app, db
from app.mod_auth.models import UserAccount, UserProfile
from sqlalchemy.exc import IntegrityError
from flask import url_for
from datetime import datetime
from flask_testing import TestCase


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

        user1_profile = UserProfile(first_name="user1", last_name="userLastname",
                                    email="user1@example.com")

        user2_profile = UserProfile(first_name="user2", last_name="user2LastName",
                                    email="user2@example.com")

        # user1 = UserAccount(username="test1hadithi", email="test1hadithi@hadithi.com",
        #                     password="password", registered_on=datetime.now())
        #
        # user2 = UserAccount(username="test2hadithi", email="test2hadithi@hadithi.com",
        #                     password="password", registered_on=datetime.now())

        try:
            db.session.add(user1_profile)
            db.session.add(user2_profile)
            db.session.commit()
        except IntegrityError as ie:
            print("Integrity Error: ", ie)
            db.session.rollback()

        return user1_profile, user2_profile

    def login(self):
        """
        Login in the user to the testing app
        :return: The authenticated user for the test app
        """
        return self.client.post(
            "auth/login",
            data=dict(email='user@example.com', password='password', confirm='password'),
            follow_redirects=True
        )


if __name__ == "__main__":
    unittest.main()