"""
Roles, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class RolForm(FlaskForm):
    """ Formulario Rol """
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
