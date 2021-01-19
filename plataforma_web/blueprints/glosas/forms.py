"""
Glosas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.autoridades.models import Autoridad


def autoridades_opciones():
    """ Autoridades: opciones para select """
    return Autoridad.query.filter(Autoridad.estatus == 'A').order_by(Autoridad.descripcion).all()


class GlosaForm(FlaskForm):
    """ Formulario Glosa """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='descripcion')
    fecha = DateField('Fecha', validators=[DataRequired()])
    juicio_tipo = StringField('Tipo de juicio', validators=[DataRequired(), Length(max=256)])
    expediente = StringField('Expediente', validators=[DataRequired(), Length(max=256)])
    url = StringField('URL', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
