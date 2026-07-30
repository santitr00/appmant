"""
Generador de tareas programadas a partir de plantillas activas.

Uso:
    from app.tareas.generador import generar_tareas_para_fecha
    creadas = generar_tareas_para_fecha(barrio_id, fecha)
"""
from datetime import date, timedelta
from app import db
from app.models import PlantillaTarea, TareaProgramada, Empleado


def _corresponde(plantilla: PlantillaTarea, fecha: date) -> bool:
    """¿La plantilla debe generar tarea en esa fecha, según su configuración actual?"""
    if plantilla.frecuencia == "semanal":
        return plantilla.dia_semana == fecha.weekday()
    return True


def _crear_tarea(plantilla: PlantillaTarea, fecha: date) -> bool:
    """
    Crea la TareaProgramada de la plantilla para esa fecha si aún no existe.
    Retorna True si la creó. No hace commit.
    """
    existe = TareaProgramada.query.filter_by(
        plantilla_id=plantilla.id, fecha=fecha
    ).first()
    if existe:
        return False

    tarea = TareaProgramada(
        plantilla_id=plantilla.id,
        fecha=fecha,
        horario=plantilla.horario,
        estado="pendiente",
        descripcion=plantilla.descripcion,
    )
    db.session.add(tarea)
    if plantilla.empleado_id:
        emp = Empleado.query.get(plantilla.empleado_id)
        if emp:
            tarea.empleados.append(emp)
    return True


def generar_tareas_para_fecha(barrio_id: int, fecha: date) -> int:
    """
    Genera TareaProgramada para las plantillas activas del barrio
    que correspondan al día `fecha`.

    - Plantillas diarias: se generan siempre.
    - Plantillas semanales: solo si fecha.weekday() == plantilla.dia_semana
      (weekday: 0=lunes … 6=domingo, igual que Python).

    Evita duplicados: si ya existe una tarea para esa plantilla y fecha, la omite.

    Retorna el número de tareas nuevas creadas.
    """
    plantillas = PlantillaTarea.query.filter_by(barrio_id=barrio_id, activa=True).all()

    creadas = 0
    for plantilla in plantillas:
        if not _corresponde(plantilla, fecha):
            continue
        if _crear_tarea(plantilla, fecha):
            creadas += 1

    if creadas:
        db.session.commit()

    return creadas


def generar_tareas_para_semana(barrio_id: int, fecha_inicio: date) -> int:
    """
    Genera tareas para los 7 días a partir de fecha_inicio.
    Retorna el total de tareas creadas.
    """
    total = 0
    for i in range(7):
        dia = fecha_inicio + timedelta(days=i)
        total += generar_tareas_para_fecha(barrio_id, dia)
    return total


# ── Reprogramación de una plantilla editada ───────────────────────────────────

def sincronizar_tareas_futuras(plantilla: PlantillaTarea, desde: date = None) -> dict:
    """
    Aplica el día/horario actual de la plantilla a las tareas programadas
    de `desde` (por defecto hoy) en adelante.

    Reglas — el historial es intocable:
      - Las tareas con fecha < `desde` NUNCA se tocan.
      - Las tareas completadas o no_realizadas NUNCA se tocan, aunque sean
        futuras: conservan su estado, asignación y justificación.
      - Solo las pendientes con fecha >= `desde` se ajustan:
          · si la fecha sigue correspondiendo al nuevo día → se actualiza el horario;
          · si ya no corresponde (cambió el día de la semana o la frecuencia)
            → se elimina, junto con su justificación si tuviera una (es una tarea
              futura que nunca llegó a ejecutarse).
      - Se regeneran las tareas faltantes en el rango ya cubierto, para que los
        nuevos días aparezcan de inmediato en el calendario diario y mensual.

    Retorna {"actualizadas": n, "eliminadas": n, "creadas": n}.
    """
    hoy = desde or date.today()
    resumen = {"actualizadas": 0, "eliminadas": 0, "creadas": 0}

    # Plantilla semanal sin día: no se puede saber qué corresponde. Se sale sin
    # tocar nada, para no borrar pendientes por una configuración incompleta.
    if plantilla.frecuencia == "semanal" and plantilla.dia_semana is None:
        return resumen

    futuras = (
        TareaProgramada.query
        .filter(
            TareaProgramada.plantilla_id == plantilla.id,
            TareaProgramada.fecha >= hoy,
        )
        .all()
    )

    # Horizonte ya generado: hasta dónde hay que rellenar los días nuevos.
    horizonte = max([t.fecha for t in futuras] + [hoy])

    for tarea in futuras:
        if tarea.estado != "pendiente":
            continue  # completada / no_realizada → historial, no se toca

        if _corresponde(plantilla, tarea.fecha):
            if tarea.horario != plantilla.horario:
                tarea.horario = plantilla.horario
                resumen["actualizadas"] += 1
        else:
            if tarea.justificacion:
                db.session.delete(tarea.justificacion)
            db.session.delete(tarea)
            resumen["eliminadas"] += 1

    db.session.flush()

    if plantilla.activa:
        dia = hoy
        while dia <= horizonte:
            if _corresponde(plantilla, dia) and _crear_tarea(plantilla, dia):
                resumen["creadas"] += 1
            dia += timedelta(days=1)

    db.session.commit()
    return resumen
