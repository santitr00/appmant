from functools import wraps
from flask import abort
from flask_login import current_user


def rol_requerido(*roles):
    """Decorador que exige que el usuario tenga uno de los roles indicados."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def solo_admin(f):
    """Solo el rol 'admin' puede acceder."""
    return rol_requerido("admin")(f)
