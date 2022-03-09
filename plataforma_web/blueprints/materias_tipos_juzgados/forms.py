"""
Materias Tipos de Juzgados, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.materias.models import Materia


def materias_opciones():
    """ Materias: opciones para select """
    return Materia.query.filter_by(estatus='A').order_by(Materia.nombre).all()


class MateriaTipoJuzgadoForm(FlaskForm):
    """ Formulario MateriaTipoJuzgado """
    materia = QuerySelectField(query_factory=materias_opciones, get_label='nombre', validators=[DataRequired()])
    clave = StringField('Clave', validators=[DataRequired(), Length(max=256)])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')
