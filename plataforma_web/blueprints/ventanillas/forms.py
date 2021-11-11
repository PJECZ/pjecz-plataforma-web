"""
Ventanillas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.autoridades.models import Autoridad


def autoridades_opciones():
    """ Autoridades: opciones para select """
    return Autoridad.query.filter_by(es_notaria=False).filter_by(estatus='A').order_by(Autoridad.clave).all()


class VentanillaForm(FlaskForm):
    """ Formulario Ventanilla """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='clave', validators=[DataRequired()])
    numero = IntegerField('Número', validators=[DataRequired()])
    guardar = SubmitField('Guardar')
