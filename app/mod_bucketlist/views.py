from flask import request, jsonify
from flask_api.exceptions import NotFound
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import db, app_logger
from app.decorators.ownership import auth_required
from . import bucketlist
from .models import BucketList


@bucketlist.route("", methods=["GET", "POST"])
@login_required
@auth_required
def bucket_lists():
    """
    Get bucket lists for the given user
    :return: JSOn response with bucketlist items for authenticated users
    """
    user_id = current_user.id
    result_data = None

    if request.method == "GET":
        results = BucketList.get_all(user_id)
        limit = int(request.args.get("limit", 20))
        query = request.args.get("q")

        try:
            page = int(request.args.get("page", 1))
        except TypeError:
            app_logger.error("Can't convert Non integer literal to int, defaulting page query to 1")
            page = 1

        # validation, ensure the page and limit args are integers
        if not isinstance(page, int):
            raise ValueError("Please specify an integer for the page request argument")

        if not isinstance(limit, int):
            raise ValueError("Please specify an integer for the limit request argument")

        # if the limit is a negative integer, we can convert it to positive
        if limit < 0:
            limit *= -1

        if page < 1:
            raise NotFound("Please specify a valid page")

        if results.all():
            result_data = results
            limit = 100 if limit > 100 else limit
            if query:
                result_data = results.filter(BucketList.name.ilike("%{0}%".format(query)))

            result_list = []
            for item in result_data.paginate(page, limit, False).items:
                if callable(getattr(item, "to_json")):
                    result = item.to_json()
                    result_list.append(result)

            return jsonify({"message": result_list})

        return jsonify({"message": "User has no bucket list"})

    if request.method == "POST":
        name = request.values.get("name")
        bucket_list = BucketList(created_by=user_id, name=name)
        try:
            db.session.add(bucket_list)
            db.session.commit()
        except IntegrityError as ie:
            app_logger.error("Cannot add bucket list item with error {}".format(ie))
            db.session.rollback()

        return jsonify(
            {
                "message": "Bucketlist was created successfully",
                "bucketlist": bucket_list.to_json()
            }), 201

    return jsonify({})
