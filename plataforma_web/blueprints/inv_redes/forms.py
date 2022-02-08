"""
Redes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class INVRedesForm(FlaskForm):
    """Formulario INVRedes"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    tipo = StringField("Tipo", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
