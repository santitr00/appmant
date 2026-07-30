from datetime import date, datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user

from app import db
from app.tareas import tareas_bp
from app.tareas.generador import generar_tareas_para_fecha, generar_tareas_para_semana
from app.tareas.forms import TareaExcepcionalForm
from app.models import TareaProgramada, TareaExcepcional, Justificacion, Empleado


def _choices_empleados(barrio_id):
    emps = (
        Empleado.query
        .filter_by(barrio_id=barrio_id, activo=True)
        .order_by(Empleado.nombre)
        .all()
    )
    return [(e.id, e.nombre) for e in emps]


def _empleados_validos(ids_raw, barrio_id):
    """Devuelve lista de objetos Empleado a partir de IDs enviados por el cliente."""
    result = []
    for raw in ids_raw:
        if str(raw).isdigit():
            emp = Empleado.query.get(int(raw))
            if emp and emp.barrio_id == barrio_id:
                result.append(emp)
    return result


# ── Generación manual ────────────────────────────────────────────────────────

@tareas_bp.route("/generar", methods=["POST"])
@login_required
def generar():
    fecha_str = request.form.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    except ValueError:
        fecha = date.today()

    creadas = generar_tareas_para_fecha(current_user.barrio_id, fecha)
    flash(f"Se generaron {creadas} tarea(s) para {fecha.strftime('%d/%m/%Y')}.", "success")
    return redirect(url_for("calendario.dia", fecha=fecha.isoformat()))


@tareas_bp.route("/generar-semana", methods=["POST"])
@login_required
def generar_semana():
    total = generar_tareas_para_semana(current_user.barrio_id, date.today())
    flash(f"Se generaron {total} tarea(s) para la semana.", "success")
    return redirect(url_for("calendario.dia"))


# ── AJAX: marcar estado de tarea programada ──────────────────────────────────

@tareas_bp.route("/programada/<int:id>/estado", methods=["POST"])
@login_required
def actualizar_estado_programada(id):
    tarea = TareaProgramada.query.get_or_404(id)
    if tarea.plantilla.barrio_id != current_user.barrio_id:
        abort(403)

    nuevo_estado = request.form.get("estado")
    if nuevo_estado not in ("completada", "no_realizada", "pendiente"):
        return jsonify({"error": "Estado inválido"}), 400

    tarea.estado = nuevo_estado
    tarea.completada_en = datetime.utcnow() if nuevo_estado == "completada" else None
    db.session.commit()
    return jsonify({"ok": True, "estado": tarea.estado})


# ── AJAX: asignar empleados en tarea programada ───────────────────────────────

@tareas_bp.route("/programada/<int:id>/asignar", methods=["POST"])
@login_required
def asignar_programada(id):
    tarea = TareaProgramada.query.get_or_404(id)
    if tarea.plantilla.barrio_id != current_user.barrio_id:
        abort(403)

    tarea.empleados = _empleados_validos(
        request.form.getlist("empleado_ids"), current_user.barrio_id
    )
    db.session.commit()
    return jsonify({"ok": True, "responsable": tarea.responsable or ""})


# ── AJAX: asignar empleados en tarea excepcional ──────────────────────────────

@tareas_bp.route("/excepcional/<int:id>/asignar", methods=["POST"])
@login_required
def asignar_excepcional(id):
    tarea = TareaExcepcional.query.get_or_404(id)
    if tarea.barrio_id != current_user.barrio_id:
        abort(403)

    tarea.empleados = _empleados_validos(
        request.form.getlist("empleado_ids"), current_user.barrio_id
    )
    db.session.commit()
    return jsonify({"ok": True, "responsable": tarea.responsable or ""})


# ── AJAX: justificación de tarea programada ──────────────────────────────────

@tareas_bp.route("/programada/<int:id>/justificar", methods=["POST"])
@login_required
def justificar_programada(id):
    tarea = TareaProgramada.query.get_or_404(id)
    if tarea.plantilla.barrio_id != current_user.barrio_id:
        abort(403)

    motivo = request.form.get("motivo", "").strip()
    if not motivo:
        return jsonify({"error": "El motivo es requerido"}), 400

    exc_id_raw = request.form.get("tarea_excepcional_id", "").strip()
    exc_id = None
    if exc_id_raw.isdigit():
        exc = TareaExcepcional.query.get(int(exc_id_raw))
        if exc and exc.barrio_id == current_user.barrio_id and exc.fecha == tarea.fecha:
            exc_id = exc.id

    if tarea.justificacion:
        tarea.justificacion.motivo = motivo
        tarea.justificacion.tarea_excepcional_id = exc_id
    else:
        db.session.add(Justificacion(
            tarea_programada_id=id,
            motivo=motivo,
            tarea_excepcional_id=exc_id,
        ))
    db.session.commit()
    return jsonify({"ok": True})


@tareas_bp.route("/programada/<int:id>/justificar/eliminar", methods=["POST"])
@login_required
def eliminar_justificacion_programada(id):
    tarea = TareaProgramada.query.get_or_404(id)
    if tarea.plantilla.barrio_id != current_user.barrio_id:
        abort(403)
    if tarea.justificacion:
        db.session.delete(tarea.justificacion)
        db.session.commit()
    return jsonify({"ok": True})


# ── Tareas excepcionales: crear ──────────────────────────────────────────────

@tareas_bp.route("/excepcional/nueva", methods=["GET", "POST"])
@login_required
def nueva_excepcional():
    form = TareaExcepcionalForm()
    form.empleado_ids.choices = _choices_empleados(current_user.barrio_id)

    if form.validate_on_submit():
        tarea = TareaExcepcional(
            barrio_id=current_user.barrio_id,
            fecha=form.fecha.data,
            horario=form.horario.data,
            descripcion=form.descripcion.data,
            creada_por=current_user.id,
            prioridad=form.prioridad.data,
            estado="pendiente",
        )
        db.session.add(tarea)
        db.session.flush()
        tarea.empleados = _empleados_validos(form.empleado_ids.data or [], current_user.barrio_id)
        db.session.commit()
        flash("Tarea excepcional creada.", "success")
        return redirect(url_for("calendario.dia", fecha=tarea.fecha.isoformat()))

    if request.method == "GET":
        fecha_pre = request.args.get("fecha", date.today().isoformat())
        try:
            form.fecha.data = date.fromisoformat(fecha_pre)
        except ValueError:
            form.fecha.data = date.today()

    return render_template("tareas/excepcional_form.html", form=form,
                           titulo="Nueva tarea excepcional")


# ── Tareas excepcionales: editar ─────────────────────────────────────────────

@tareas_bp.route("/excepcional/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_excepcional(id):
    tarea = TareaExcepcional.query.get_or_404(id)
    if tarea.barrio_id != current_user.barrio_id:
        abort(403)

    form = TareaExcepcionalForm(obj=tarea)
    form.empleado_ids.choices = _choices_empleados(current_user.barrio_id)

    if request.method == "GET":
        form.empleado_ids.data = [e.id for e in tarea.empleados]

    if form.validate_on_submit():
        tarea.descripcion = form.descripcion.data
        tarea.fecha = form.fecha.data
        tarea.horario = form.horario.data
        tarea.prioridad = form.prioridad.data
        tarea.empleados = _empleados_validos(form.empleado_ids.data or [], current_user.barrio_id)
        db.session.commit()
        flash("Tarea excepcional actualizada.", "success")
        return redirect(url_for("calendario.dia", fecha=tarea.fecha.isoformat()))

    return render_template("tareas/excepcional_form.html", form=form,
                           titulo="Editar tarea excepcional", tarea=tarea)


# ── Tareas excepcionales: eliminar ───────────────────────────────────────────

@tareas_bp.route("/excepcional/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar_excepcional(id):
    tarea = TareaExcepcional.query.get_or_404(id)
    if tarea.barrio_id != current_user.barrio_id:
        abort(403)

    fecha = tarea.fecha
    if tarea.justificacion:
        tarea.justificacion.tarea_excepcional_id = None
    db.session.delete(tarea)
    db.session.commit()
    flash("Tarea excepcional eliminada.", "info")
    return redirect(url_for("calendario.dia", fecha=fecha.isoformat()))


# ── AJAX: marcar estado de tarea excepcional ─────────────────────────────────

@tareas_bp.route("/excepcional/<int:id>/estado", methods=["POST"])
@login_required
def actualizar_estado_excepcional(id):
    tarea = TareaExcepcional.query.get_or_404(id)
    if tarea.barrio_id != current_user.barrio_id:
        abort(403)

    nuevo_estado = request.form.get("estado")
    if nuevo_estado not in ("completada", "pendiente"):
        return jsonify({"error": "Estado inválido"}), 400

    tarea.estado = nuevo_estado
    tarea.completada_en = datetime.utcnow() if nuevo_estado == "completada" else None
    db.session.commit()
    return jsonify({"ok": True, "estado": tarea.estado})
