from . import auth
from flask import request
from .security_utils import send_mail, confirm_token, generate_confirmation_token
from flask_login import login_required, login_user, current_user, logout_user
from app import db


@auth.route('/login/', methods=["POST", "GET"])
def login():
    """
    Login route for user's to login to their accounts
    :return: Login view
    """
    return "login"


@auth.route('/register/', methods=["POST", "GET"])
def register():
    return "register"
