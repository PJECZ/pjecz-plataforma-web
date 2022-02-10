"""
Soportes Categorias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional



class SoporteCategoriaForm(FlaskForm):
    """ Formulario SoporteCategoria """
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    instrucciones = TextAreaField('Instrucciones', validators=[Optional(), Length(max=2048)])
    guardar = SubmitField('Guardar')
