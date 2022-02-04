"""
Oficinas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TimeField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

class OficinaForm(FlaskForm):
    """ Formulario Oficina """
    clave = StringField('Clave', validators=[DataRequired(), Length(max=32)])
    descripcion = StringField('Descripción', validators=[Optional(), Length(max=512)])
    descripcion_corta = StringField('Descripción Corta', validators=[Optional(), Length(max=64)])
    es_juridiccional = BooleanField('Juridiccional')
    apertura = TimeField('Horario de apertura', validators=[DataRequired()], format="%H:%M")
    cierre = TimeField('Horario de cierre', validators=[DataRequired()], format="%H:%M")
    limite_personas = IntegerField('Límite de personas', validators=[Optional()])

    guardar = SubmitField('Guardar')
