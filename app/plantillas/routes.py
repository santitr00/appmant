from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.plantillas import plantillas_bp
from app.plantillas.forms import PlantillaForm
from app.models import PlantillaTarea, Empleado
from app.auth.decorators import solo_admin


def _choices_empleados(barrio_id):
    emps = (
        Empleado.query
        .filter_by(barrio_id=barrio_id, activo=True)
        .order_by(Empleado.nombre)
        .all()
    )
    return [(0, "— Sin responsable habitual —")] + [(e.id, e.nombre) for e in emps]


@plantillas_bp.route("/")
@login_required
@solo_admin
def index():
    plantillas = (
        PlantillaTarea.query
        .filter_by(barrio_id=current_user.barrio_id)
        .order_by(PlantillaTarea.activa.desc(), PlantillaTarea.nombre)
        .all()
    )
    return render_template("plantillas/index.html", plantillas=plantillas)


@plantillas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
@solo_admin
def nueva():
    form = PlantillaForm()
    form.empleado_id.choices = _choices_empleados(current_user.barrio_id)

    if form.validate_on_submit():
        dia = form.dia_semana.data
        plantilla = PlantillaTarea(
            barrio_id=current_user.barrio_id,
            nombre=form.nombre.data.strip(),
            descripcion=form.descripcion.data,
            frecuencia=form.frecuencia.data,
            dia_semana=int(dia) if dia != "" else None,
            horario=form.horario.data,
            activa=form.activa.data,
            empleado_id=form.empleado_id.data or None,
        )
        db.session.add(plantilla)
        db.session.commit()
        flash(f'Plantilla "{plantilla.nombre}" creada correctamente.', "success")
        return redirect(url_for("plantillas.index"))
    return render_template("plantillas/form.html", form=form, titulo="Nueva plantilla")


@plantillas_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@solo_admin
def editar(id):
    plantilla = PlantillaTarea.query.get_or_404(id)
    if plantilla.barrio_id != current_user.barrio_id:
        abort(403)

    form = PlantillaForm(obj=plantilla)
    form.empleado_id.choices = _choices_empleados(current_user.barrio_id)

    if plantilla.dia_semana is not None:
        form.dia_semana.data = str(plantilla.dia_semana)

    if form.validate_on_submit():
        plantilla.nombre = form.nombre.data.strip()
        plantilla.descripcion = form.descripcion.data
        plantilla.frecuencia = form.frecuencia.data
        dia = form.dia_semana.data
        plantilla.dia_semana = int(dia) if dia not in ("", None) else None
        plantilla.horario = form.horario.data
        plantilla.activa = form.activa.data
        plantilla.empleado_id = form.empleado_id.data or None
        db.session.commit()
        flash(f'Plantilla "{plantilla.nombre}" actualizada.', "success")
        return redirect(url_for("plantillas.index"))

    return render_template(
        "plantillas/form.html", form=form, titulo="Editar plantilla", plantilla=plantilla
    )


@plantillas_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
@solo_admin
def toggle_activa(id):
    plantilla = PlantillaTarea.query.get_or_404(id)
    if plantilla.barrio_id != current_user.barrio_id:
        abort(403)
    plantilla.activa = not plantilla.activa
    db.session.commit()
    estado = "activada" if plantilla.activa else "desactivada"
    flash(f'Plantilla "{plantilla.nombre}" {estado}.', "info")
    return redirect(url_for("plantillas.index"))
