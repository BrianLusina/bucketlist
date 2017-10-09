from . import bucketlist
from flask import request
from flask_api.exceptions import NotFound, PermissionDenied, AuthenticationFailed, ParseError
from flask_login import login_required, current_user
from .models import BucketList, BucketListItem


@bucketlist.route("", methods=["GET", "POST"])
@login_required
def bucket_lists():
    """
    Get bucket lists for the given user
    :return: JSOn response with bucketlist items for authenticated users
    """
    user_id = current_user.id
    result_date = None

    if request.method == "GET":
        results = BucketList.get_all(user_id)
        limit = request.args.get("limit", 20)
        query = request.args.get("q")
        page = request.args.get("page")
        if page < 1:
            raise NotFound("Please specify a valid page")

    return "bucketlist"
