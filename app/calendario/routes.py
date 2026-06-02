import calendar as cal_module
from collections import defaultdict
from datetime import date, timedelta
from flask import render_template, request, jsonify, url_for
from flask_login import login_required, current_user

from app.models import TareaProgramada, TareaExcepcional, PlantillaTarea, Empleado
from app.tareas.generador import generar_tareas_para_fecha
from app.calendario import calendario_bp

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def fecha_es(d: date) -> str:
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month]} de {d.year}"


# ── Vista diaria ─────────────────────────────────────────────────────────────

@calendario_bp.route("/")
@calendario_bp.route("/dia")
@login_required
def dia():
    fecha_str = request.args.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    except ValueError:
        fecha = date.today()

    today = date.today()

    generar_tareas_para_fecha(current_user.barrio_id, fecha)

    tareas_prog = (
        TareaProgramada.query
        .join(PlantillaTarea)
        .filter(
            PlantillaTarea.barrio_id == current_user.barrio_id,
            TareaProgramada.fecha == fecha,
        )
        .order_by(TareaProgramada.horario)
        .all()
    )

    tareas_exc = (
        TareaExcepcional.query
        .filter_by(barrio_id=current_user.barrio_id, fecha=fecha)
        .order_by(TareaExcepcional.horario)
        .all()
    )

    fecha_anterior = fecha - timedelta(days=1)
    fecha_siguiente = fecha + timedelta(days=1)

    empleados_lista = (
        Empleado.query
        .filter_by(barrio_id=current_user.barrio_id, activo=True)
        .order_by(Empleado.nombre)
        .all()
    )

    return render_template(
        "calendario/dia.html",
        fecha=fecha,
        today=today,
        fecha_label=fecha_es(fecha),
        tareas_prog=tareas_prog,
        tareas_exc=tareas_exc,
        fecha_anterior=fecha_anterior,
        fecha_siguiente=fecha_siguiente,
        empleados_lista=empleados_lista,
    )


# ── Vista semanal ─────────────────────────────────────────────────────────────

@calendario_bp.route("/semana")
@login_required
def semana():
    fecha_str = request.args.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    except ValueError:
        fecha = date.today()

    lunes = fecha - timedelta(days=fecha.weekday())
    dias_semana = [lunes + timedelta(days=i) for i in range(7)]

    for d in dias_semana:
        generar_tareas_para_fecha(current_user.barrio_id, d)

    semana_data = []
    for d in dias_semana:
        prog = (
            TareaProgramada.query
            .join(PlantillaTarea)
            .filter(
                PlantillaTarea.barrio_id == current_user.barrio_id,
                TareaProgramada.fecha == d,
            )
            .order_by(TareaProgramada.horario)
            .all()
        )
        exc = (
            TareaExcepcional.query
            .filter_by(barrio_id=current_user.barrio_id, fecha=d)
            .order_by(TareaExcepcional.horario)
            .all()
        )
        semana_data.append({
            "fecha": d,
            "fecha_label": fecha_es(d),
            "dia_nombre": DIAS_ES[d.weekday()],
            "tareas_prog": prog,
            "tareas_exc": exc,
            "completadas": sum(1 for t in prog if t.estado == "completada"),
            "no_realizadas": sum(1 for t in prog if t.estado == "no_realizada"),
            "pendientes": sum(1 for t in prog if t.estado == "pendiente"),
        })

    domingo = lunes + timedelta(days=6)
    semana_anterior = lunes - timedelta(days=7)
    semana_siguiente = lunes + timedelta(days=7)

    return render_template(
        "calendario/semana.html",
        semana_data=semana_data,
        lunes=lunes,
        domingo=domingo,
        semana_anterior=semana_anterior,
        semana_siguiente=semana_siguiente,
        today=date.today(),
        MESES_ES=MESES_ES,
    )


# ── Vista mensual ─────────────────────────────────────────────────────────────

@calendario_bp.route("/mes")
@login_required
def mes():
    today = date.today()
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
        if not (1 <= month <= 12):
            raise ValueError
    except (ValueError, TypeError):
        year, month = today.year, today.month

    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    return render_template(
        "calendario/mes.html",
        year=year,
        month=month,
        nombre_mes=MESES_ES[month].capitalize(),
        today=today,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
    )


# ── API JSON para FullCalendar ────────────────────────────────────────────────

@calendario_bp.route("/api/mes")
@login_required
def api_mes():
    start_str = request.args.get("start", "")
    end_str = request.args.get("end", "")

    try:
        start = date.fromisoformat(start_str[:10])
        end = date.fromisoformat(end_str[:10])
    except (ValueError, TypeError, IndexError):
        today = date.today()
        start = today.replace(day=1)
        _, ld = cal_module.monthrange(today.year, today.month)
        end = today.replace(day=ld) + timedelta(days=1)

    barrio_id = current_user.barrio_id

    prog_list = (
        TareaProgramada.query
        .join(PlantillaTarea)
        .filter(
            PlantillaTarea.barrio_id == barrio_id,
            TareaProgramada.fecha >= start,
            TareaProgramada.fecha < end,
        )
        .all()
    )
    exc_list = TareaExcepcional.query.filter(
        TareaExcepcional.barrio_id == barrio_id,
        TareaExcepcional.fecha >= start,
        TareaExcepcional.fecha < end,
    ).all()

    prog_by_date = defaultdict(list)
    for t in prog_list:
        prog_by_date[t.fecha].append(t)

    exc_by_date = defaultdict(list)
    for t in exc_list:
        exc_by_date[t.fecha].append(t)

    all_dates = set(prog_by_date.keys()) | set(exc_by_date.keys())

    events = []
    for d in sorted(all_dates):
        prog = prog_by_date[d]
        exc = exc_by_date[d]

        completadas = sum(1 for t in prog if t.estado == "completada")
        no_realizadas = sum(1 for t in prog if t.estado == "no_realizada")
        pendientes = sum(1 for t in prog if t.estado == "pendiente")

        if no_realizadas > 0:
            color = "#dc3545"
        elif pendientes == 0 and completadas > 0:
            color = "#198754"
        elif completadas > 0:
            color = "#fd7e14"
        else:
            color = "#6c757d"

        text_color = "#000" if color == "#ffc107" else "#fff"

        parts = []
        if completadas:
            parts.append(f"{completadas} ok")
        if no_realizadas:
            parts.append(f"{no_realizadas} no")
        if pendientes:
            parts.append(f"{pendientes} pend.")
        if exc:
            parts.append(f"{len(exc)} exc.")

        events.append({
            "title": "  ".join(parts),
            "start": d.isoformat(),
            "url": url_for("calendario.dia", fecha=d.isoformat()),
            "backgroundColor": color,
            "borderColor": color,
            "textColor": text_color,
        })

    return jsonify(events)
