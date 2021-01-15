"""
Listas de Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class ListaDeAcuerdoForm(FlaskForm):
    """ Formulario Lista de Acuerdo """
    # fecha
    descripcion = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    # archivo_nombre
    guardar = SubmitField('Guardar')
