from flask import Blueprint


auth = Blueprint(name="auth", import_name=__name__, url_prefix="/auth", static_folder="static",
                 template_folder="templates")

from . import views
