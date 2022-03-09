"""
Funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from lib.safe_string import CURP_REGEXP

from plataforma_web.blueprints.domicilios.models import Domicilio


def domicilios_opciones():
    """Domicilios: opciones para select"""
    return Domicilio.query.filter_by(estatus="A").order_by(Domicilio.completo).all()


class FuncionarioForm(FlaskForm):
    """Formulario Funcionario"""

    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[DataRequired(), Length(min=18, max=18), Regexp(CURP_REGEXP, 0, "CURP inválida")])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[DataRequired(), Email()])
    en_funciones = BooleanField("En funciones", validators=[Optional()])
    en_sentencias = BooleanField("En sentencias", validators=[Optional()])
    en_soportes = BooleanField("En soportes", validators=[Optional()])
    en_tesis_jurisprudencias = BooleanField("En tesis y jurisprudencias", validators=[Optional()])
    guardar = SubmitField("Guardar")


class FuncionarioSearchForm(FlaskForm):
    """Formulario de búsqueda de Funcionarios"""

    nombres = StringField("Nombres", validators=[Optional(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[Optional(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(max=18)])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")


class FuncionarioDomicilioForm(FlaskForm):
    """Formulario para relacionar oficinas al funcionario a partir de una direccion"""

    funcionario_nombre = StringField("Nombre")  # Read only
    funcionario_curp = StringField("CURP")  # Read only
    funcionario_puesto = StringField("Puesto")  # Read only
    funcionario_email = StringField("e-mail")  # Read only
    domicilio = QuerySelectField(query_factory=domicilios_opciones, get_label="completo")
    asignar = SubmitField("Asignar")
