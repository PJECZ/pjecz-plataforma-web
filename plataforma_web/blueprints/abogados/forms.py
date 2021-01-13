"""
Abogados, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class AbogadoForm(FlaskForm):
    """ Formulario abogado """
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
