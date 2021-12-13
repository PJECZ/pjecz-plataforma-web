"""
Tesis-funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia


def funcionarios_opciones():
    """Funcionarios: opciones para select"""
    return Funcionario.query.filter_by(en_tesis_jurisprudencias=True).filter_by(estatus="A").order_by(Funcionario.nombres).all()


def tesis_opciones():
    """Tesis y jursprudencias: opciones para select"""
    return TesisJurisprudencia.query.filter_by(estatus="A").order_by(TesisJurisprudencia.clave_control).all()


class TesisFuncionarioForm(FlaskForm):
    """Formulario TesisFuncionario"""

    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label="nombre", validators=[DataRequired()])
    tesis = QuerySelectField(query_factory=tesis_opciones, get_label="clave_control", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class TesisFuncionarioWithFuncionarioForm(FlaskForm):
    """Formulario TesisFuncionario"""

    funcionario = StringField("Funcionario")  # Solo lectura
    tesis = QuerySelectField(query_factory=tesis_opciones, get_label="clave_control", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class TesisFuncionarioWithTesisForm(FlaskForm):
    """Formulario TesisFuncionario"""

    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label="nombre", validators=[DataRequired()])
    tesis = StringField("Tesis")  # Solo lectura
    guardar = SubmitField("Guardar")
