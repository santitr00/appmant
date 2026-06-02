from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.empleados import empleados_bp
from app.empleados.forms import EmpleadoForm
from app.models import Empleado
from app.auth.decorators import solo_admin


@empleados_bp.route("/")
@login_required
@solo_admin
def index():
    empleados = (
        Empleado.query
        .filter_by(barrio_id=current_user.barrio_id)
        .order_by(Empleado.activo.desc(), Empleado.nombre)
        .all()
    )
    return render_template("empleados/index.html", empleados=empleados)


@empleados_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@solo_admin
def nuevo():
    form = EmpleadoForm()
    if form.validate_on_submit():
        emp = Empleado(
            barrio_id=current_user.barrio_id,
            nombre=form.nombre.data.strip(),
            activo=form.activo.data,
        )
        db.session.add(emp)
        db.session.commit()
        flash(f'Empleado "{emp.nombre}" agregado correctamente.', "success")
        return redirect(url_for("empleados.index"))
    return render_template("empleados/form.html", form=form, titulo="Nuevo empleado")


@empleados_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@solo_admin
def editar(id):
    emp = Empleado.query.get_or_404(id)
    if emp.barrio_id != current_user.barrio_id:
        abort(403)

    form = EmpleadoForm(obj=emp)
    if form.validate_on_submit():
        emp.nombre = form.nombre.data.strip()
        emp.activo = form.activo.data
        db.session.commit()
        flash(f'Empleado "{emp.nombre}" actualizado.', "success")
        return redirect(url_for("empleados.index"))

    return render_template("empleados/form.html", form=form, titulo="Editar empleado", empleado=emp)


@empleados_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
@solo_admin
def toggle_activo(id):
    emp = Empleado.query.get_or_404(id)
    if emp.barrio_id != current_user.barrio_id:
        abort(403)
    emp.activo = not emp.activo
    db.session.commit()
    estado = "activado" if emp.activo else "desactivado"
    flash(f'Empleado "{emp.nombre}" {estado}.', "info")
    return redirect(url_for("empleados.index"))
