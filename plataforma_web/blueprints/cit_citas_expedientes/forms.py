"""
Cit Citas Expedientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Optional


class CitCitaExpedienteSearchForm(FlaskForm):
    """Formulario para buscar Expedientes"""

    expediente = StringField("Expediente", validators=[Optional(), Length(max=16)])
    buscar = SubmitField("Buscar")
