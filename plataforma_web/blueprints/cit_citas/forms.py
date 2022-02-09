"""
CITAS Citas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional


class CITCitaSearchForm(FlaskForm):
    """Formulario para buscar Citas"""

    inicio_tiempo = DateTimeField("Tiempo de inicio", validators=[Optional()])
    buscar = SubmitField("Buscar")
