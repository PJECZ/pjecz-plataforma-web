"""
Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, Optional

from estadisticas.blueprints.distritos.models import Distrito


def distritos_opciones():
    """ Distritos: opciones para select """
    return Distrito.query.filter(Distrito.estatus == 'A').order_by(Distrito.nombre).all()


class AutoridadForm(FlaskForm):
    """ Formulario Autoridad """
    distrito = QuerySelectField(query_factory=distritos_opciones, get_label='nombre')
    descripcion = StringField('Autoridad', validators=[DataRequired(), Length(max=256)])
    email = StringField('e-mail', validators=[Optional(), Email()])
    guardar = SubmitField('Guardar')
