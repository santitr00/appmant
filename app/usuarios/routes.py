from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.usuarios import usuarios_bp
from app.usuarios.forms import UsuarioForm
from app.models import Usuario
from app.auth.decorators import solo_admin


@usuarios_bp.route("/")
@login_required
@solo_admin
def index():
    usuarios = (
        Usuario.query
        .filter_by(barrio_id=current_user.barrio_id)
        .order_by(Usuario.activo.desc(), Usuario.nombre)
        .all()
    )
    return render_template("usuarios/index.html", usuarios=usuarios)


@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@solo_admin
def nuevo():
    form = UsuarioForm()
    if form.validate_on_submit():
        # Verificar DNI único
        if Usuario.query.filter_by(dni=form.dni.data.strip()).first():
            flash("Ya existe un usuario con ese DNI.", "danger")
            return render_template("usuarios/form.html", form=form, titulo="Nuevo usuario")

        u = Usuario(
            barrio_id=current_user.barrio_id,
            nombre=form.nombre.data.strip(),
            dni=form.dni.data.strip(),
            email=form.email.data.strip() or None,
            rol=form.rol.data,
            activo=form.activo.data,
        )
        if form.password.data:
            u.set_password(form.password.data)
        else:
            flash("Debe ingresar una contraseña.", "danger")
            return render_template("usuarios/form.html", form=form, titulo="Nuevo usuario")

        db.session.add(u)
        db.session.commit()
        flash(f'Usuario "{u.nombre}" creado correctamente.', "success")
        return redirect(url_for("usuarios.index"))

    return render_template("usuarios/form.html", form=form, titulo="Nuevo usuario")


@usuarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@solo_admin
def editar(id):
    u = Usuario.query.get_or_404(id)
    if u.barrio_id != current_user.barrio_id:
        abort(403)

    form = UsuarioForm(obj=u)
    form.password.validators = []   # contraseña opcional en edición

    if form.validate_on_submit():
        # Verificar DNI único (excluyendo al propio usuario)
        existente = Usuario.query.filter_by(dni=form.dni.data.strip()).first()
        if existente and existente.id != u.id:
            flash("Ya existe otro usuario con ese DNI.", "danger")
            return render_template("usuarios/form.html", form=form, titulo="Editar usuario", usuario=u)

        u.nombre = form.nombre.data.strip()
        u.dni = form.dni.data.strip()
        u.email = form.email.data.strip() or None
        u.rol = form.rol.data
        u.activo = form.activo.data
        if form.password.data:
            u.set_password(form.password.data)
        db.session.commit()
        flash(f'Usuario "{u.nombre}" actualizado.', "success")
        return redirect(url_for("usuarios.index"))

    return render_template("usuarios/form.html", form=form, titulo="Editar usuario", usuario=u)


@usuarios_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
@solo_admin
def toggle_activo(id):
    u = Usuario.query.get_or_404(id)
    if u.barrio_id != current_user.barrio_id:
        abort(403)
    if u.id == current_user.id:
        flash("No podés desactivar tu propia cuenta.", "warning")
        return redirect(url_for("usuarios.index"))
    u.activo = not u.activo
    db.session.commit()
    estado = "activado" if u.activo else "desactivado"
    flash(f'Usuario "{u.nombre}" {estado}.', "info")
    return redirect(url_for("usuarios.index"))
