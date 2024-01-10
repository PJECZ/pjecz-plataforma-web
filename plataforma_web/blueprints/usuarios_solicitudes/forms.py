"""
Usuarios-solicitudes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length


class UsuarioSolicitudNewForm(FlaskForm):
    """Formulario UsuarioRol"""

    usuario_nombre = StringField("Usuario Nombre")  # Read only
    usuario_email = StringField("Usuario email")  # Read only
    email_personal = StringField("E-Mail Personal", validators=[Length(max=64)])
    telefono_celular = StringField("Teléfono Celular", validators=[Length(max=16)])
    enviar = SubmitField("Enviar")


class UsuarioSolicitudValidateTokenForm(FlaskForm):
    """Formulario UsuarioRol"""

    usuario_nombre = StringField("Usuario Nombre")  # Read only
    usuario_email = StringField("Usuario email")  # Read only
    email_personal = StringField("E-Mail Personal")  # Read only
    telefono_celular = StringField("Teléfono Celular")  # Read only
    token_email = StringField("Token - E-Mail Personal", validators=[Length(max=6)])
    token_telefono_celular = StringField("Token - Teléfono Cellular", validators=[Length(max=6)])
    enviar = SubmitField("Enviar")
