"""
CITAS Clientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Optional


class CITExpedienteSearchForm(FlaskForm):
    """Formulario para buscar Expedientes"""

    expediente = StringField("Expediente", validators=[Optional(), Length(max=16)])
    buscar = SubmitField("Buscar")
