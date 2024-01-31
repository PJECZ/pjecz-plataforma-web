"""
Usuarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from lib.safe_string import CONTRASENA_REGEXP, CURP_REGEXP

from plataforma_web.blueprints.oficinas.models import Oficina
from plataforma_web.blueprints.usuarios.models import Usuario

CONTRASENA_MENSAJE = "De 8 a 48 caracteres con al menos una mayúscula, una minúscula y un número. No acentos, ni eñe."


def oficinas_opciones():
    """Oficinas: opciones para select"""
    return Oficina.query.filter_by(estatus="A").order_by(Oficina.clave).all()


class AccesoForm(FlaskForm):
    """Formulario de acceso al sistema"""

    siguiente = HiddenField()
    identidad = StringField("Correo electrónico o usuario", validators=[Optional(), Length(8, 256)])
    contrasena = PasswordField("Contraseña", validators=[Optional(), Length(8, 48), Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE)])
    email = StringField("Correo electrónico", validators=[Optional(), Email()])
    token = StringField("Token", validators=[Optional()])
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


class UsuarioNewForm(FlaskForm):
    """Formulario para nuevo usuario"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    oficina = QuerySelectField(query_factory=oficinas_opciones, get_label="clave_nombre")
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Regexp(CURP_REGEXP), Length(max=18)])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[DataRequired(), Email()])
    workspace = SelectField("Workspace", choices=Usuario.WORKSPACES, validators=[DataRequired()])
    efirma_registro_id = IntegerField("ID de registro en eFirma", validators=[Optional()])
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


class UsuarioEditForm(FlaskForm):
    """Formulario para editar usuario"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    oficina = QuerySelectField(query_factory=oficinas_opciones, get_label="clave_nombre")
    nombres = StringField("Nombres", validators=[Optional(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[Optional(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Regexp(CURP_REGEXP), Length(max=18)])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail")  # Read only
    workspace = StringField("Workspace")  # Read only
    efirma_registro_id = IntegerField("ID de registro en eFirma", validators=[Optional()])
    guardar = SubmitField("Guardar")


class UsuarioEditAdminForm(FlaskForm):
    """Formulario para editar usuario"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    oficina = QuerySelectField(query_factory=oficinas_opciones, get_label="clave_nombre")
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Regexp(CURP_REGEXP), Length(max=18)])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[DataRequired(), Email()])
    workspace = SelectField("Workspace", choices=Usuario.WORKSPACES, validators=[DataRequired()])
    efirma_registro_id = IntegerField("ID de registro en eFirma", validators=[Optional()])
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


class UsuarioSearchForm(FlaskForm):
    """Formulario para buscar usuarios"""

    nombres = StringField("Nombres", validators=[Optional(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[Optional(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(max=18)])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
