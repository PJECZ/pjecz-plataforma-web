"""
Distritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class DistritoForm(FlaskForm):
    """ Formulario Distrito """

    nombre = StringField("Distrito", validators=[DataRequired(), Length(max=256)])
    es_distrito_judicial = BooleanField("Es distrito judicial", validators=[Optional()])
    guardar = SubmitField("Guardar")
