"""
Autoridades Funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.funcionarios.models import Funcionario


def autoridades_opciones():
    """ Autoridades: opciones para select """
    return Autoridad.query.filter_by(es_notaria=False).filter_by(estatus='A').order_by(Autoridad.clave).all()


def funcionarios_opciones():
    """ Funcionarios: opciones para select """
    return Funcionario.query.filter_by(estatus='A').order_by(Funcionario.nombres).all()


class AutoridadFuncionarioForm(FlaskForm):
    """ Formulario AutoridadFuncionario """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='clave', validators=[DataRequired()])
    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label='nombre', validators=[DataRequired()])
    guardar = SubmitField('Guardar')


class AutoridadFuncionarioWithAutoridadForm(FlaskForm):
    """ Formulario AutoridadFuncionario """
    autoridad = StringField("Autoridad")  # Solo lectura
    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label='nombre', validators=[DataRequired()])
    guardar = SubmitField('Guardar')


class AutoridadFuncionarioWithFuncionarioForm(FlaskForm):
    """ Formulario AutoridadFuncionario """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='clave', validators=[DataRequired()])
    funcionario = StringField("Funcionario")  # Solo lectura
    guardar = SubmitField('Guardar')
