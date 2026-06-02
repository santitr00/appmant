from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    dni = StringField(
        "DNI",
        validators=[DataRequired(message="Campo requerido."), Length(min=4, max=20)],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="Campo requerido."), Length(min=4)],
    )
    recordarme = BooleanField("Recordarme")
    submit = SubmitField("Ingresar")
