"""
Centros de Trabjo, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.domicilios.models import Domicilio


def distritos_opciones():
    """Distrito: opciones para select"""
    return Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()


def domicilios_opciones():
    """ Domicilios: opciones para select """
    return Domicilio.query.filter_by(estatus='A').order_by(Domicilio.completo).all()


class CentroTrabajoForm(FlaskForm):
    """Formulario CentroTrabajo"""

    clave = StringField("Clave")  # Read only
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    telefono = StringField("Teléfono", validators=[DataRequired(), Length(max=256)])
    distrito = QuerySelectField("Distrito", query_factory=distritos_opciones, get_label="nombre", validators=[DataRequired()])
    domicilio = QuerySelectField("Domicilio", query_factory=domicilios_opciones, get_label="completo", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class CentroTrabajoSearchForm(FlaskForm):
    """ Formulario para buscar Centros de Trabajo """
    clave = StringField("Clave", validators=[Optional(), Length(max=16)])
    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    buscar = SubmitField('Buscar')
