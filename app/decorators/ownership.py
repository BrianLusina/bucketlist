"""
Contains decorator functions that will be used for authentication purposes. These functions
are used to check whether a bucketlist item corresponds to a User or whether a bucket list
 item, belongs to a bucket list
"""
import jwt
from app.mod_auth.models import UserAccount, Session
from app.mod_bucketlist.models import BucketListItem, BucketList
from flask import request, current_app
from flask.ext.sqlalchemy import sqlalchemy
from functools import wraps
from flask_api.exceptions import AuthenticationFailed, PermissionDenied, NotFound
from app.exceptions.handler import ValidationError
from flask_login import current_user


def owned_by_user(f):
    """
    Force a model to be owned by a user
    :param f function we are wrapping
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        bucketlist_id = kwargs.get('id')
        bucketlist = BucketList.query.get(int(bucketlist_id))

        if bucketlist.created_by != current_user.id:
            raise PermissionDenied()
        return f(*args, **kwargs)
    return decorated


def owned_by_bucketlist(f):
    """
     Check that an item is owned by a bucket list
    Force an item to be owned by a BucketList
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        bucketlist_id = kwargs.get('id')
        bucketlistitem_id = kwargs.get('item_id')
        bucketlist_item = BucketListItem.query.get(int(bucketlistitem_id))
        if bucketlist_item:
            try:
                assert bucketlist_item.bucketlist_id == int(bucketlist_id)
            except:
                raise NotFound()
        kwargs['item'] = bucketlist_item
        return f(*args, **kwargs)
    return decorated


def auth_required(f):
    """
    This forces clients to authenticate before they are given access to resources
    :param f: function to decorate
    :return: decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            jwt_token = request.headers.get('Authorization')
            secret_key = current_app.config.get('SECRET_KEY')

            if jwt_token is None:
                raise PermissionDenied("You need to pass your token as a header")

            try:
                decoded_jwt = jwt.decode(jwt_token[7:], secret_key)
            except jwt.ExpiredSignatureError:
                raise PermissionDenied('Your token has expired! Please login again')
            UserAccount.query.filter_by(
                username=decoded_jwt['username'],
                password=decoded_jwt['password']).first()
            if not Session.query.filter_by(token=jwt_token[7:]):
                raise AuthenticationFailed()

        except (sqlalchemy.orm.exc.MultipleResultsFound, sqlalchemy.orm.exc.NoResultFound) as e:
            print("Error Validating token => ", e)
            raise ValidationError()
        return f(*args, **kwargs)
    return decorated
