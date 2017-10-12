from flask_api.exceptions import APIException


class NullBucketListException(APIException):
    """Raises exception when trying to edit non existing bucketlist item"""
    status_code = 404
    detail = 'No such bucketlist. You can only access an existing bucketlist'


class NullReferenceException(APIException):
    """Raises exception when trying to edit non existing bucketlist item"""
    status_code = 404
    detail = 'No such item in your bucketlist. \
        You can only edit/update existing items'