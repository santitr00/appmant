from flask import Blueprint

tareas_bp = Blueprint("tareas", __name__, template_folder="templates")

from app.tareas import routes  # noqa: F401, E402
