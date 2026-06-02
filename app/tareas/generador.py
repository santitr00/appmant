"""
Generador de tareas programadas a partir de plantillas activas.

Uso:
    from app.tareas.generador import generar_tareas_para_fecha
    creadas = generar_tareas_para_fecha(barrio_id, fecha)
"""
from datetime import date
from app import db
from app.models import PlantillaTarea, TareaProgramada, Empleado


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
    dia_semana = fecha.weekday()
    plantillas = PlantillaTarea.query.filter_by(barrio_id=barrio_id, activa=True).all()

    creadas = 0
    for plantilla in plantillas:
        if plantilla.frecuencia == "semanal" and plantilla.dia_semana != dia_semana:
            continue

        # Verificar si ya existe
        existe = TareaProgramada.query.filter_by(
            plantilla_id=plantilla.id, fecha=fecha
        ).first()
        if existe:
            continue

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
        creadas += 1

    if creadas:
        db.session.commit()

    return creadas


def generar_tareas_para_semana(barrio_id: int, fecha_inicio: date) -> int:
    """
    Genera tareas para los 7 días a partir de fecha_inicio.
    Retorna el total de tareas creadas.
    """
    from datetime import timedelta

    total = 0
    for i in range(7):
        dia = fecha_inicio + timedelta(days=i)
        total += generar_tareas_para_fecha(barrio_id, dia)
    return total
