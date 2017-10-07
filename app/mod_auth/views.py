from flask import request, jsonify

from app import db
from . import auth
from .exceptions import UserAlreadyExists
from .models import UserAccount


@auth.route('/login/', methods=["POST", "GET"])
def login():
    """
    Login route for user's to login to their accounts
    :return: Login view
    """
    return "login"


@auth.route('/register/', methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return jsonify({"message": "Welcome to BucketList Service",
                        "more": "To register make a POST with username and password to /auth/register/"}), 200
    else:
        username = request.values.get("username")
        password = request.values.get("password")
        email = request.values.get("email")
        if username and password:
            user_account = UserAccount.query.filter_by(username=username).first()
            if user_account is not None:
                raise UserAlreadyExists()
            else:
                user_account = UserAccount(username=username, email=email, password=password)
                db.session.add(user_account)
                db.session.commit()
                return jsonify({
                    "message": "Registered successfully",
                    "more": "Login using POST to /auth/login/"
                }), 201

    return jsonify({}), 200
