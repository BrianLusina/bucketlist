"""
The email confirmation should contain a unique URL that a user simply needs to click in 
order to confirm his/her account 
url will be something like this http://<base_url>/confirm.
The key here is the id. We are going to encode the user email (along with a timestamp) in the id using the itsdangerous package.
"""
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app import mail
from flask_mail import Message


def send_mail(to, subject, template):
    """
    Sends a confirmation tmail to the new registering user
    :param to: recipient of this email, the new registering user
    :param subject: The subject of the email
    :param template: The message body
    """
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender=current_app.config.get("MAIL_DEFAULT_SENDER")
    )
    mail.send(msg)


def generate_confirmation_token(email):
    """
    Generates a confirmation token for the user to confirm their account
    The actual email is encoded in the token
    :param email: The user email
    :return:
    """
    serializer = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY"))
    return serializer.dumps(email, salt=current_app.config.get("SECURITY_PASSWORD_SALT"))


def confirm_token(token):
    """
    we use the loads() method, which takes the token and expiration period
    :param token:
    :return: An email as long as the token has not expired
    """
    serializer = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY"))
    email = serializer.loads(
            token,
            salt=current_app.config.get("SECURITY_PASSWORD_SALT"),
            max_age=86400
        )
    return email
