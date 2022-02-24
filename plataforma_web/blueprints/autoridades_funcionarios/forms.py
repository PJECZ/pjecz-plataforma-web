"""
Autoridades Funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired

from plataforma_web.blueprints.autoridades.models import Autoridad


def autoridades_opciones():
    """ Autoridades: opciones para select """
    return Autoridad.query.filter_by(es_notaria=False).filter_by(estatus='A').order_by(Autoridad.clave).all()


class AutoridadFuncionarioWithFuncionarioForm(FlaskForm):
    """ Formulario AutoridadFuncionario """
    autoridad = QuerySelectField(query_factory=autoridades_opciones, get_label='clave', validators=[DataRequired()])
    funcionario = StringField("Funcionario")  # Read only
    guardar = SubmitField('Guardar')
