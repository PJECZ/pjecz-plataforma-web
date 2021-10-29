"""
Autoridades Funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.funcionarios.models import Funcionario


def autoridades_opciones():
    """ Autoridades: opciones para select """
    return Autoridad.query.filter_by(estatus='A').order_by(Autoridad.clave).all()


def funcionarios_opciones():
    """ Funcionarios: opciones para select """
    return Funcionario.query.filter_by(estatus='A').order_by(Funcionario.nombre).all()


class AutoridadFuncionarioForm(FlaskForm):
    """ Formulario AutoridadFuncionario """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='nombre')
    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label='nombre')
    guardar = SubmitField('Guardar')
