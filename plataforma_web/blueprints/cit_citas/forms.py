"""
Citas Citas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateTimeField
from wtforms.validators import Optional


class CitCitaSearchForm(FlaskForm):
    """Formulario para buscar Citas"""

    inicio_tiempo = DateTimeField("Tiempo de inicio", validators=[Optional()])
    buscar = SubmitField("Buscar")
