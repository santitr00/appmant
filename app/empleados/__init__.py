from flask import Blueprint

empleados_bp = Blueprint("empleados", __name__)

from app.empleados import routes  # noqa: F401, E402
