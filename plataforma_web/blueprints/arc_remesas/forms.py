"""
Archivo - Remesas, formularios
"""
from flask_wtf import FlaskForm
from datetime import date
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class ArcRemesaNewForm(FlaskForm):
    """Formulario nueva Remesa"""

    num_oficio = StringField("Núm. Oficio", validators=[Optional(), Length(max=16)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1950, date.today().year)])
    crear = SubmitField("Crear")
