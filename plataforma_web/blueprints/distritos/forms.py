"""
Distritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class DistritoForm(FlaskForm):
    """ Formulario Distrito """
    nombre = StringField('Distrito', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
