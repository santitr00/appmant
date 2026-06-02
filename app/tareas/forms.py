from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SelectMultipleField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class TareaExcepcionalForm(FlaskForm):
    descripcion = TextAreaField(
        "Descripción",
        validators=[DataRequired(message="Campo requerido."), Length(max=1000)],
    )
    fecha = DateField("Fecha", validators=[DataRequired()])
    horario = TimeField("Horario", validators=[DataRequired()])
    prioridad = SelectField(
        "Prioridad",
        choices=[("baja", "Baja"), ("media", "Media"), ("alta", "Alta")],
        default="media",
    )
    empleado_ids = SelectMultipleField(
        "Responsables",
        coerce=int,
        validators=[Optional()],
    )
    submit = SubmitField("Guardar tarea")


class JustificacionForm(FlaskForm):
    motivo = TextAreaField(
        "Motivo / justificación",
        validators=[DataRequired(message="Campo requerido."), Length(max=500)],
    )
    submit = SubmitField("Guardar justificación")
