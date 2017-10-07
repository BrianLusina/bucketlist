# coding=utf-8
"""
This defines the application module that essentially creates a new flask app object
"""
import logging
import os
from datetime import datetime

import jinja2
from flask import Flask, g
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config

# initialize objects of flask extensions that will be used and then initialize the application
# once the flask object has been created and initialized. 1 caveat for this is that when
# configuring Celery, the broker will remain constant for all configurations
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"

mail = Mail()
app_logger = logging.getLogger("BucketListApiLogger")


class BucketListApp(Flask):
    """
    Custom application class subclassing Flask application. This is to ensure more modularity in
     terms of static files and templates. This way a module will have its own templates and the
      root template folder will be more modularized and easier to manage
    """

    def __init__(self):
        """
        jinja_loader object (a FileSystemLoader pointing to the global templates folder) is
        being replaced with a ChoiceLoader object that will first search the normal
        FileSystemLoader and then check a PrefixLoader that we create
        """
        Flask.__init__(self, __name__, static_folder="static", template_folder="templates")
        self.jinja_loader = jinja2.ChoiceLoader([
            self.jinja_loader,
            jinja2.PrefixLoader({}, delimiter=".")
        ])

    def create_global_jinja_loader(self):
        """
        Overriding to return the loader set up in __init__
        :return: jinja_loader 
        """
        return self.jinja_loader

    def register_blueprint(self, blueprint, **options):
        """
        Overriding to add the blueprints names to the prefix loader's mapping
        :param blueprint: 
        :param options: 
        """
        Flask.register_blueprint(self, blueprint, **options)
        self.jinja_loader.loaders[1].mapping[blueprint.name] = blueprint.jinja_loader


def create_app(config_name):
    """
    Creates a new flask app instance with the given configuration
    :param config_name: configuration to use when creating the application 
    :return: a new WSGI Flask app
    :rtype: Flask
    """
    app = BucketListApp()

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # initialize the db and login manager
    db.init_app(app)
    login_manager.init_app(app)

    error_handlers(app)
    register_app_blueprints(app)
    app_request_handlers(app, db)
    app_logger_handler(app, config_name)

    # initialize mail
    mail.init_app(app)

    # this will reduce the load time for templates and increase the application performance
    app.jinja_env.cache = {}

    return app


def app_request_handlers(app, db_):
    """
    This will handle all the requests sent to the application
    This will include before and after requests which could be used to update a user's status or the 
    database that is currently in use
    :param app: the current flask app
    """

    @app.before_request
    def before_request():
        """
        Before submitting the request, change the currently logged in user 'last seen' status to now
        this will update the database last_seen column and every time the user makes a request (refreshes the
        page), the last seen will be updated. this is called before any request is ma
        """
        g.user = current_user
        if current_user.is_authenticated:
            current_user.last_seen = datetime.now()
            db.session.add(g.user)
            db_.session.add(current_user)
            db_.session.commit()


def app_logger_handler(app, config_name):
    """
    Will handle error logging for the application and will store the app log files in a file that can 
    later be accessed.
    :param app: current flask application
    """
    from logging.handlers import SMTPHandler, RotatingFileHandler
    mail_server = app.config.get("MAIL_SERVER")

    if app.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    if config_name == "production":
        if not app.debug and mail_server != "":
            credentials = None

            mail_username = app.config.get("MAIL_USERNAME")
            mail_password = app.config.get("MAIL_PASSWORD")

            if mail_username or mail_password:
                credentials = (mail_username, mail_password)

            mail_handler = SMTPHandler(mailhost=(mail_server, app.config.get("MAIL_HOST")),
                                       fromaddr="no-reply@" + mail_server,
                                       toaddrs=app.config.get("ADMINS"),
                                       subject="App failure",
                                       credentials=credentials)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not app.debug and os.environ.get("HEROKU") is None:
            # log file will be saved in the tmp directory
            file_handler = RotatingFileHandler(filename="tmp/app.log", mode="a", maxBytes=1 * 1024 * 1024,
                                               backupCount=10)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%('
                                                        'lineno)d]'))
            app.logger.setLevel(logging.INFO)
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.info("App")


def error_handlers(app):
    """
    Error handlers function that will initialize error handling templates for the entire application
    :param app: the flask app
    """
    from flask import render_template

    @app.errorhandler(404)
    def not_found(error):
        """
        This will handle errors that involve 404 messages
        :return: a template instructing user they have sent a request that does not exist on
         the server
        """
        app_logger.error('An error occurred during a request. Error => {}'.format(error))
        return render_template("errors/404.html"), error

    @app.errorhandler(500)
    def server_error(e):
        # Log the error and stacktrace.
        app_logger.error('An error occurred during a request. Error => {}'.format(e))
        return render_template("errors/500.html"), e

    @app.errorhandler(403)
    def error_403(error):
        app_logger.error('An error occurred during a request. Error => {}'.format(error))
        return render_template("errors/403.html"), error

    @app.errorhandler(400)
    def not_found(error):
        app_logger.error('An error occurred during a request. Error => {}'.format(error))
        return render_template('errors/400.html'), error


def register_app_blueprints(app_):
    """
    Registers the application blueprints
    :param app_: the current flask app
    """
    from app.mod_auth import auth

    app_.register_blueprint(auth)
