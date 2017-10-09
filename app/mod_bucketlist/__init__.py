from flask import Blueprint

bucketlist = Blueprint(name="bucketlist", import_name=__name__, url_prefix="/bucketlists/")

from . import views
