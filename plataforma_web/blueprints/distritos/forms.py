"""
Distritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class DistritoForm(FlaskForm):
    """ Formulario Distrito """

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    nombre_corto = StringField("Nombre corto", validators=[Optional(), Length(max=64)])
    es_distrito_judicial = BooleanField("Es judicial", validators=[Optional()])
    guardar = SubmitField("Guardar")
