"""
Peritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class PeritoForm(FlaskForm):
    """ Formulario Perito """
    tipo = StringField('Tipo', validators=[DataRequired(), Length(max=256)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    domicilio = StringField('Domicilio', validators=[DataRequired(), Length(max=256)])
    telefono_fijo = StringField('Teléfono fijo', validators=[Optional(), Length(max=256)])
    telefono_celular = StringField('Teléfono celular', validators=[Optional(), Length(max=256)])
    email = StringField('e-mail', validators=[Optional(), Email()])
    guardar = SubmitField('Guardar')
