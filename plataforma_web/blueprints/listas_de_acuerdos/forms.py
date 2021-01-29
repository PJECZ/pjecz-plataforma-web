"""
Listas de Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.autoridades.models import Autoridad


def autoridades_opciones():
    """ Autoridades: opciones para select """
    return Autoridad.query.filter(Autoridad.estatus == 'A').order_by(Autoridad.descripcion).all()


class ListaDeAcuerdoNewForm(FlaskForm):
    """ Formulario Lista de Acuerdo """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='descripcion')
    fecha = DateField('Fecha', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=256)])
    archivo = StringField('Archivo', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    guardar = SubmitField('Guardar')


class ListaDeAcuerdoEditForm(FlaskForm):
    """ Formulario Lista de Acuerdo """
    fecha = DateField('Fecha', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=256)])
    archivo = StringField('Archivo', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    guardar = SubmitField('Guardar')
