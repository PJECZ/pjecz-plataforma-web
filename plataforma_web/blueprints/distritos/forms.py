"""
Distritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class DistritoForm(FlaskForm):
    """Formulario Distrito"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
