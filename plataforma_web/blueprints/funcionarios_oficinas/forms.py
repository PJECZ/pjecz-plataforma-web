"""
Funcionarios Oficinas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.oficinas.models import Oficina


def oficinas_opciones():
    """ Oficinas: opciones para select """
    return Oficina.query.filter_by(estatus="A").order_by(Oficina.clave).all()


class FuncionarioOficinaForm(FlaskForm):
    """ Formulario FuncionarioOficina """
    funcionario = StringField('Funcionario')  # Read only
    oficina = QuerySelectField(query_factory=oficinas_opciones, get_label="clave_nombre")
    guardar = SubmitField('Guardar')
