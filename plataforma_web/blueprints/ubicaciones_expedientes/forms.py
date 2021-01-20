"""
Ubicacines de Expedientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import  StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class Ubicacion_ExpedienteForm(FlaskForm):
    """ Formulario Ubicación de Expediente """
    expediente = StringField('Expediente', validators=[DataRequired(), Length(max=256)])
    ubicacion = StringField('Ubicación', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')

