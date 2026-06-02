from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config_map

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(env_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_map[env_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder."
    login_manager.login_message_category = "warning"

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from app.auth import auth_bp
    from app.plantillas import plantillas_bp
    from app.tareas import tareas_bp
    from app.calendario import calendario_bp
    from app.usuarios import usuarios_bp
    from app.reportes import reportes_bp
    from app.empleados import empleados_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(plantillas_bp, url_prefix="/plantillas")
    app.register_blueprint(tareas_bp, url_prefix="/tareas")
    app.register_blueprint(calendario_bp, url_prefix="/calendario")
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
    app.register_blueprint(reportes_bp, url_prefix="/reportes")
    app.register_blueprint(empleados_bp, url_prefix="/empleados")

    # Ruta raíz → redirige al calendario
    from flask import redirect, url_for

    @app.route("/")
    def index():
        return redirect(url_for("calendario.dia"))

    return app
