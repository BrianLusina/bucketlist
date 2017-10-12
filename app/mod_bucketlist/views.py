from flask import request, jsonify
from flask_api.exceptions import NotFound
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from .exceptions import NullBucketListException, NullReferenceException
from app import db, app_logger
from app.decorators.ownership import auth_required, owned_by_bucketlist, owned_by_user
from . import bucketlist
from .models import BucketList, BucketListItem
import json


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


@bucketlist.route("<int:bucket_list_id>", methods=["GET", "PUT", "DELETE"])
@login_required
@auth_required
def edit_bucketlist(bucket_list_id, **kwargs):
    """
    Route that gets, edits or deletes a given bucketlist with its id.
    :param bucket_list_id: id of the bucket list in question
    :param kwargs: used when editing the given bucket list
    :return: either the bucket list if it is a GET request, Success message if deletion is
    successful or if editing has been successful
    :rtype: dict
    """
    bucket_list = BucketList.query.get(bucket_list_id)

    # if we can not get a bucket list, return an error message
    if not bucket_list:
        raise NullBucketListException()

    if request.method == "DELETE":
        db.session.delete(bucket_list)
        db.session.commit()
        return jsonify({
            "message": "Bucketlist was deleted successfully"
        }), 200

    if request.method == "PUT":
        name = request.values.get("name")
        bucket_list.name = name
        db.session.add(bucket_list)
        db.session.commit()

        return jsonify({
            "message": "Bucketlist edited successfully!"
        }), 200

    # else we return the bucket list item
    return jsonify(**bucket_list.to_json()), 200


@bucketlist.route("<int:bucket_list_id>/items", methods=["POST", "GET"])
@login_required
@auth_required
@owned_by_user
def create_or_get_bucketlist_items(bucket_list_id):
    """
    Gets bucket list items for a particular bucket given its id. Handles POST and GET
     requests,
     POST requests will handle updating of a bucket list items and GET will handle the
     retrieval of bucket list items
    :param bucket_list_id: id of the bucket list to retrieve
    :return: Bucket list items as a JSON response
    :rtype: dict
    """
    bucketlist = BucketList.query.get(bucket_list_id)

    if bucketlist is None:
        raise NullBucketListException()

    bucket_list_items = bucketlist.items

    if request.method == "GET":
        return jsonify({
            "message": "{} bucket list items".format(bucketlist.name),
            "items": [item.to_json() for item in bucket_list_items]
        }), 200

    if request.method == "POST":
        name = request.values.get("name")
        bucketlist_item = BucketListItem(bucket_list_id, name)
        db.session.add(bucketlist_item)
        db.session.commit()

        return jsonify({
            "message": "BucketList item added successfully.",
            "bucketlistitem": bucketlist_item.to_json()
        }), 201


@bucketlist.route("<int:bucket_list_id>/items/<int:item_id>", methods=["GET", "PUT",
                                                                       "DELETE"])
@login_required
@owned_by_user
@owned_by_bucketlist
def get_modify_bucket_list_item(bucket_list_id, item_id, **kwargs):
    """
    Route handling modification of a bucketlist item for a given bucket list
    Has decorators that ensure only logged in uses can access this route, that only users
    who own this bucketlist can modify it and that this bucketlist item is owned by a give
    bucketlist.
    :param bucket_list_id: Bucketlist id
    :param item_id: Item id for a given bucket list item
    :return: Response for operation
    :rtype: dict
    """
    bucket_list_item = BucketListItem.query.get(int(item_id))
    bucketlist = BucketList.query.get(bucket_list_id)

    if bucket_list_item is None:
        raise NullReferenceException()

    if request.method == "GET":
        return jsonify({
            "bucketlist": bucketlist.to_json(),
            "bucketlist_item": bucket_list_item.to_json()
        })

    # editing a given bucket list item
    if request.method == "PUT":
        name = request.values.get("name")
        done = request.values.get("done")
        bucket_list_item.done = done

        db.session.add(bucket_list_item)
        db.session.commit()

        return jsonify({
            "message": "Successfully edited bucketlist item",
            "bucketlist item": bucket_list_item.to_json()
        }), 200

    if request.method == "DELETE":
        db.session.delete(bucket_list_item)
        db.session.commit()
        return jsonify({"message": "Bucketlist item was successfully deleted"}), 200
