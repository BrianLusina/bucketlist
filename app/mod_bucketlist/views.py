from . import bucketlist
from flask import request
from flask_login import login_required, current_user


@bucketlist.route("", methods=["GET", "POST"])
@login_required
def bucket_lists():
    """
    Get bucket lists for the given user
    :return:
    """
    pass
