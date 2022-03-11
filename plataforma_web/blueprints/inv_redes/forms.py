"""
Redes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.inv_redes.models import InvRedes


class InvRedesForm(FlaskForm):
    """Formulario InvRedes"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    tipo = SelectField("Tipo", choices=InvRedes.TIPOS, validators=[DataRequired()])
    guardar = SubmitField("Guardar")
