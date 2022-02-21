"""
Funcionarios Oficinas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.oficinas.models import Oficina


def oficinas_opciones():
    """ Oficinas: opciones para select """
    return Oficina.query.filter_by(estatus="A").order_by(Oficina.descripcion).all()


class FuncionarioOficinaForm(FlaskForm):
    """ Formulario FuncionarioOficina """
    usuario = StringField('Usuario')  # Read only
    oficina = QuerySelectField(query_factory=oficinas_opciones, get_label="descripcion")
    guardar = SubmitField('Guardar')
