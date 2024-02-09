"""
Usuarios Datos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato


class UsuarioDatoEditEstadoCivilForm(FlaskForm):
    """Formulario UsuarioDatoEditEstadoCivil"""

    estado_civil = SelectField("Estado Civil", choices=UsuarioDato.ESTADOS_CIVILES, validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoValidateForm(FlaskForm):
    """Formulario para validar"""

    mensaje = StringField("Mensaje", validators=[Optional()])
    valido = SubmitField("Válido")
    no_valido = SubmitField("No Válido")
