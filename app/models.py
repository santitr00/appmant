from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Barrio(db.Model):
    __tablename__ = "barrios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    logo_path = db.Column(db.String(255), nullable=True)
    color_primario = db.Column(db.String(7), default="#2563eb")
    activo = db.Column(db.Boolean, default=True, nullable=False)

    usuarios = db.relationship("Usuario", back_populates="barrio", lazy="dynamic")
    plantillas = db.relationship("PlantillaTarea", back_populates="barrio", lazy="dynamic")
    tareas_excepcionales = db.relationship("TareaExcepcional", back_populates="barrio", lazy="dynamic")
    empleados = db.relationship("Empleado", back_populates="barrio", lazy="dynamic")

    def __repr__(self):
        return f"<Barrio {self.nombre}>"


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    barrio_id = db.Column(db.Integer, db.ForeignKey("barrios.id"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(180), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.Enum("admin", "usuario", name="rol_usuario"), nullable=False, default="usuario")
    activo = db.Column(db.Boolean, default=True, nullable=False)

    barrio = db.relationship("Barrio", back_populates="usuarios")
    tareas_exc_creadas = db.relationship(
        "TareaExcepcional", foreign_keys="TareaExcepcional.creada_por", back_populates="creador"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def es_admin(self):
        return self.rol == "admin"

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Usuario {self.dni} [{self.rol}]>"


class Empleado(db.Model):
    __tablename__ = "empleados"

    id = db.Column(db.Integer, primary_key=True)
    barrio_id = db.Column(db.Integer, db.ForeignKey("barrios.id"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    barrio = db.relationship("Barrio", back_populates="empleados")

    def __repr__(self):
        return f"<Empleado {self.nombre}>"


# ── Tablas de asociación M2M ──────────────────────────────────────────────────

tarea_programada_empleados = db.Table(
    'tarea_programada_empleados',
    db.Column('tarea_id',    db.Integer, db.ForeignKey('tareas_programadas.id',  ondelete='CASCADE'), primary_key=True),
    db.Column('empleado_id', db.Integer, db.ForeignKey('empleados.id',           ondelete='CASCADE'), primary_key=True),
)

tarea_excepcional_empleados = db.Table(
    'tarea_excepcional_empleados',
    db.Column('tarea_id',    db.Integer, db.ForeignKey('tareas_excepcionales.id', ondelete='CASCADE'), primary_key=True),
    db.Column('empleado_id', db.Integer, db.ForeignKey('empleados.id',            ondelete='CASCADE'), primary_key=True),
)


class PlantillaTarea(db.Model):
    __tablename__ = "plantillas_tarea"

    DIAS_SEMANA = [
        (0, "Lunes"), (1, "Martes"), (2, "Miércoles"), (3, "Jueves"),
        (4, "Viernes"), (5, "Sábado"), (6, "Domingo"),
    ]

    id = db.Column(db.Integer, primary_key=True)
    barrio_id = db.Column(db.Integer, db.ForeignKey("barrios.id"), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    frecuencia = db.Column(
        db.Enum("diaria", "semanal", name="frecuencia_tarea"), nullable=False, default="diaria"
    )
    dia_semana = db.Column(db.Integer, nullable=True)
    horario = db.Column(db.Time, nullable=False)
    activa = db.Column(db.Boolean, default=True, nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=True)

    barrio = db.relationship("Barrio", back_populates="plantillas")
    tareas_programadas = db.relationship("TareaProgramada", back_populates="plantilla", lazy="dynamic")
    empleado = db.relationship("Empleado", foreign_keys=[empleado_id])

    @property
    def dia_semana_nombre(self):
        if self.dia_semana is None:
            return "-"
        return dict(self.DIAS_SEMANA).get(self.dia_semana, "-")

    def __repr__(self):
        return f"<Plantilla {self.nombre}>"


class TareaProgramada(db.Model):
    __tablename__ = "tareas_programadas"

    id = db.Column(db.Integer, primary_key=True)
    plantilla_id = db.Column(db.Integer, db.ForeignKey("plantillas_tarea.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    asignado_a = db.Column(db.String(150), nullable=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=True)
    estado = db.Column(
        db.Enum("pendiente", "completada", "no_realizada", name="estado_programada"),
        default="pendiente", nullable=False,
    )
    descripcion = db.Column(db.Text, nullable=True)
    completada_en = db.Column(db.DateTime, nullable=True)

    plantilla = db.relationship("PlantillaTarea", back_populates="tareas_programadas")
    justificacion = db.relationship("Justificacion", back_populates="tarea_programada", uselist=False)
    empleado = db.relationship("Empleado", foreign_keys=[empleado_id])
    empleados = db.relationship("Empleado", secondary=tarea_programada_empleados, lazy="select")

    @property
    def responsable(self):
        if self.empleados:
            return ", ".join(e.nombre for e in self.empleados)
        if self.empleado:
            return self.empleado.nombre
        return self.asignado_a

    def __repr__(self):
        return f"<TareaProgramada {self.plantilla_id} {self.fecha}>"


class TareaExcepcional(db.Model):
    __tablename__ = "tareas_excepcionales"

    id = db.Column(db.Integer, primary_key=True)
    barrio_id = db.Column(db.Integer, db.ForeignKey("barrios.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    asignado_a = db.Column(db.String(150), nullable=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey("empleados.id"), nullable=True)
    creada_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    prioridad = db.Column(
        db.Enum("baja", "media", "alta", name="prioridad_tarea"),
        default="media", nullable=False,
    )
    estado = db.Column(
        db.Enum("pendiente", "completada", name="estado_excepcional"),
        default="pendiente", nullable=False,
    )
    completada_en = db.Column(db.DateTime, nullable=True)

    barrio = db.relationship("Barrio", back_populates="tareas_excepcionales")
    creador = db.relationship("Usuario", foreign_keys=[creada_por], back_populates="tareas_exc_creadas")
    justificacion = db.relationship("Justificacion", back_populates="tarea_excepcional", uselist=False)
    empleado = db.relationship("Empleado", foreign_keys=[empleado_id])
    empleados = db.relationship("Empleado", secondary=tarea_excepcional_empleados, lazy="select")

    @property
    def responsable(self):
        if self.empleados:
            return ", ".join(e.nombre for e in self.empleados)
        if self.empleado:
            return self.empleado.nombre
        return self.asignado_a

    def __repr__(self):
        return f"<TareaExcepcional {self.descripcion[:30]} {self.fecha}>"


class NotaDiaria(db.Model):
    __tablename__ = "notas_diarias"
    __table_args__ = (
        db.UniqueConstraint("barrio_id", "fecha", name="uq_nota_barrio_fecha"),
    )

    id = db.Column(db.Integer, primary_key=True)
    barrio_id = db.Column(db.Integer, db.ForeignKey("barrios.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    creada_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    barrio = db.relationship("Barrio")
    autor = db.relationship("Usuario", foreign_keys=[creada_por])

    def __repr__(self):
        return f"<NotaDiaria barrio={self.barrio_id} {self.fecha}>"


class Justificacion(db.Model):
    __tablename__ = "justificaciones"

    id = db.Column(db.Integer, primary_key=True)
    tarea_programada_id = db.Column(db.Integer, db.ForeignKey("tareas_programadas.id"), nullable=True)
    tarea_excepcional_id = db.Column(db.Integer, db.ForeignKey("tareas_excepcionales.id"), nullable=True)
    motivo = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    tarea_programada = db.relationship("TareaProgramada", back_populates="justificacion")
    tarea_excepcional = db.relationship("TareaExcepcional", back_populates="justificacion")

    def __repr__(self):
        return f"<Justificacion {self.id}>"
