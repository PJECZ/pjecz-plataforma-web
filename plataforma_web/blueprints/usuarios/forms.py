"""
Usuarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp

from lib.safe_string import CONTRASENA_REGEXP

CONTRASENA_MENSAJE = "De 8 a 48 caracteres con al menos una mayúscula, una minúscula y un número. No acentos, ni eñe."


class AccesoForm(FlaskForm):
    """Formulario de acceso al sistema"""

    siguiente = HiddenField()
    identidad = StringField("Correo electrónico o usuario", validators=[Optional(), Length(8, 256)])
    contrasena = PasswordField("Contraseña", validators=[Optional(), Length(8, 48), Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE)])
    email = StringField("Correo electrónico", validators=[Optional(), Email()])
    token = StringField("Token", validators=[Optional()])
    guardar = SubmitField("Guardar")


class UsuarioFormNew(FlaskForm):
    """Formulario para nuevo usuario"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[DataRequired(), Email()])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    contrasena = PasswordField(
        "Contraseña",
        validators=[
            Optional(),
            Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE),
            EqualTo("contrasena_repetir", message="Las contraseñas deben coincidir."),
        ],
    )
    contrasena_repetir = PasswordField("Repetir contraseña", validators=[Optional()])
    guardar = SubmitField("Guardar")


class UsuarioFormEdit(FlaskForm):
    """Formulario para editar usuario"""

    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[DataRequired(), Email()])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    contrasena = PasswordField(
        "Contraseña",
        validators=[
            Optional(),
            Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE),
            EqualTo("contrasena_repetir", message="Las contraseñas deben coincidir."),
        ],
    )
    contrasena_repetir = PasswordField("Repetir contraseña", validators=[Optional()])
    guardar = SubmitField("Guardar")


class CambiarContrasenaForm(FlaskForm):
    """Formulario para cambiar la contraseña"""

    contrasena_actual = PasswordField(
        "Contraseña actual",
        validators=[
            DataRequired(),
            Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE),
        ],
    )
    contrasena = PasswordField(
        "Nueva contraseña",
        validators=[
            DataRequired(),
            Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE),
            EqualTo("contrasena_repetir", message="Las contraseñas deben coincidir."),
        ],
    )
    contrasena_repetir = PasswordField("Repetir la nueva contraseña")
    actualizar = SubmitField("Actualizar")
