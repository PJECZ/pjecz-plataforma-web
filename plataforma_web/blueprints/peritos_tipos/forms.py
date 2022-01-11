"""
Peritos Tipos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class PeritoTipoForm(FlaskForm):
    """ Formulario PeritoTipo """
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
