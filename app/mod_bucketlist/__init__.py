from flask import Blueprint

bucketlist = Blueprint(name="bucketlist", import_name=__name__, url_prefix="/bucketlist/")

from . import views
