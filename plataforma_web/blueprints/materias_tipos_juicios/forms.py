"""
Materias Tipos de Juicios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class MateriaTipoJuicioForm(FlaskForm):
    """ Formulario MateriaTipoJuicio """
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
