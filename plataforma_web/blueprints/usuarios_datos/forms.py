"""
Usuarios Datos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato


class UsuarioDatoEditEstadoCivilForm(FlaskForm):
    """Formulario UsuarioDatoEditEstadoCivl"""

    estado_civil = SelectField("Estado Civil", choices=UsuarioDato.ESTADOS_CIVILES, validators=[DataRequired()])
    guardar = SubmitField("Guardar")
