from flask import Blueprint

usuarios_bp = Blueprint("usuarios", __name__, template_folder="templates")

from app.usuarios import routes  # noqa: F401, E402
