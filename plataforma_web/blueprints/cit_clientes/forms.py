"""
CITAS Clientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp, EqualTo
from lib.safe_string import CONTRASENA_REGEXP

CONTRASENA_MENSAJE = "De 8 a 48 caracteres con al menos una mayúscula, una minúscula y un número. No acentos, ni eñe."


class CITClientesForm(FlaskForm):
    """ Formulario CITClientes Nuevo Cliente """
    nombres = StringField('Nombres', validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField('Apellido Materno', validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(max=18)])
    #domicilio_id = IntegerField("Domicilio", validators=[Optional()])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=64)])
    email = StringField("Correo electrónico", validators=[Optional(), Email()])
    contrasena = PasswordField(
        "Contraseña",
        validators=[
            Optional(),
            Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE),
            EqualTo("contrasena_repetir", message="Las contraseñas deben coincidir."),
        ],
    )
    contrasena_repetir = PasswordField("Repetir contraseña", validators=[Optional()])

    guardar = SubmitField('Guardar')


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
