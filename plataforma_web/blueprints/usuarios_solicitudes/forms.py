"""
Usuarios-solicitudes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired, Regexp, Email

TELEFONO_CELULAR_REGEX = r"^\d{10}$"
TOKEN_REGEX = r"^\d{6}$"


class UsuarioSolicitudNewForm(FlaskForm):
    """Formulario UsuarioRol"""

    usuario_nombre = StringField("Tu nombre completo")  # Read only
    usuario_email = StringField("Tu correo electrónico institucional")  # Read only
    email_personal = StringField("Correo electrónico personal", validators=[DataRequired(), Email()])
    telefono_celular = StringField("Teléfono celular", validators=[DataRequired(), Regexp(TELEFONO_CELULAR_REGEX)])
    enviar = SubmitField("Enviar")


class UsuarioSolicitudValidateTokenEmailForm(FlaskForm):
    """Formulario UsuarioRol"""

    usuario_nombre = StringField("Tu nombre completo")  # Read only
    usuario_email = StringField("Tu correo electrónico institucional")  # Read only
    email_personal = StringField("Correo electrónico personal")  # Read only
    token_email = StringField("Token recibido", validators=[DataRequired(), Regexp(TOKEN_REGEX)])
    validar = SubmitField("Validar")


class UsuarioSolicitudValidateTokenTelefonoCelularForm(FlaskForm):
    """Formulario UsuarioRol"""

    usuario_nombre = StringField("Tu nombre completo")  # Read only
    usuario_email = StringField("Tu correo electrónico institucional")  # Read only
    telefono_celular = StringField("Teléfono Celular")  # Read only
    token_telefono_celular = StringField("Token recibido", validators=[DataRequired(), Regexp(TOKEN_REGEX)])
    validar = SubmitField("Validar")
