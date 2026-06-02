from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class EmpleadoForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(message="Campo requerido."), Length(max=120)],
    )
    activo = BooleanField("Empleado activo", default=True)
    submit = SubmitField("Guardar")
