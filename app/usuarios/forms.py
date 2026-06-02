from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email


class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(message="Campo requerido."), Length(max=120)],
    )
    dni = StringField(
        "DNI (se usa para iniciar sesión)",
        validators=[DataRequired(message="Campo requerido."), Length(min=4, max=20)],
    )
    email = StringField(
        "Email (opcional)",
        validators=[Optional(), Email(message="Email inválido."), Length(max=180)],
    )
    password = PasswordField(
        "Contraseña",
        validators=[Length(min=4, message="Mínimo 4 caracteres.")],
    )
    rol = SelectField(
        "Rol",
        choices=[("usuario", "Usuario"), ("admin", "Administrador")],
        default="usuario",
    )
    activo = BooleanField("Cuenta activa", default=True)
    submit = SubmitField("Guardar")
