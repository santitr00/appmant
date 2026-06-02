from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.models import Usuario


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("calendario.dia"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(dni=form.dni.data.strip()).first()
        if usuario and usuario.activo and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.recordarme.data)
            next_page = request.args.get("next")
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            return redirect(next_page or url_for("calendario.dia"))
        flash("Credenciales incorrectas o usuario inactivo.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
