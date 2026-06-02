from flask import Blueprint

plantillas_bp = Blueprint("plantillas", __name__, template_folder="templates")

from app.plantillas import routes  # noqa: F401, E402
