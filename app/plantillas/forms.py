from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, TimeField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Length, Optional


class PlantillaForm(FlaskForm):
    nombre = StringField(
        "Nombre de la tarea",
        validators=[DataRequired(message="Campo requerido."), Length(max=150)],
    )
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=1000)])
    frecuencia = SelectField(
        "Frecuencia",
        choices=[("diaria", "Diaria"), ("semanal", "Semanal")],
        validators=[DataRequired()],
    )
    dia_semana = SelectField(
        "Día de la semana",
        choices=[
            ("", "— Solo para frecuencia semanal —"),
            ("0", "Lunes"),
            ("1", "Martes"),
            ("2", "Miércoles"),
            ("3", "Jueves"),
            ("4", "Viernes"),
            ("5", "Sábado"),
            ("6", "Domingo"),
        ],
        validators=[Optional()],
    )
    horario = TimeField("Horario", validators=[DataRequired(message="Campo requerido.")])
    empleado_id = SelectField(
        "Responsable habitual",
        coerce=int,
        validators=[Optional()],
    )
    activa = BooleanField("Plantilla activa", default=True)
    submit = SubmitField("Guardar")
