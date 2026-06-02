from flask import Blueprint

calendario_bp = Blueprint("calendario", __name__, template_folder="templates")

from app.calendario import routes  # noqa: F401, E402
