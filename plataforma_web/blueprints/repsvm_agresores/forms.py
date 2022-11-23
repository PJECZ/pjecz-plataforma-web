"""
REPSVM Agresores, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from lib.safe_string import URL_REGEXP

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias_tipos_juzgados.models import MateriaTipoJuzgado
from plataforma_web.blueprints.repsvm_delitos_especificos.models import REPSVMDelitoEspecifico
from plataforma_web.blueprints.repsvm_tipos_sentencias.models import REPSVMTipoSentencia


def distritos_opciones():
    """Distritos: opciones para select"""
    return Distrito.query.filter_by(estatus="A").filter_by(es_distrito_judicial=True).order_by(Distrito.nombre).all()


def materias_tipos_juzgados_opciones():
    """Materias Tipos Juzgados: opciones para select"""
    return MateriaTipoJuzgado.query.filter_by(estatus="A").order_by(MateriaTipoJuzgado.clave).all()


def repsvm_delitos_especificos_opciones():
    """REPSVM Delitos Especificos: opciones para select"""
    return REPSVMDelitoEspecifico.query.filter_by(estatus="A").order_by(REPSVMDelitoEspecifico.descripcion).all()


def repsvm_tipos_sentencias_opciones():
    """REPSVM Tipos Sentencias: opciones para select"""
    return REPSVMTipoSentencia.query.filter_by(estatus="A").order_by(REPSVMTipoSentencia.nombre).all()


class REPSVMAgresorForm(FlaskForm):
    """Formulario REPSVMAgresor"""

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre", validators=[DataRequired()])
    materia_tipo_juzgado = QuerySelectField("Tipo de Juzgado", query_factory=materias_tipos_juzgados_opciones, get_label="descripcion", validators=[DataRequired()])
    numero_causa = StringField("Numero de causa", validators=[DataRequired(), Length(max=256)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    repsvm_delito_especifico = QuerySelectField("Delito Específico", query_factory=repsvm_delitos_especificos_opciones, get_label="descripcion", validators=[DataRequired()])
    repsvm_tipo_sentencia = QuerySelectField("Tipo de Sentencia", query_factory=repsvm_tipos_sentencias_opciones, get_label="nombre", validators=[DataRequired()])
    pena_impuesta = StringField("Pena impuesta", validators=[DataRequired(), Length(max=256)])
    observaciones = TextAreaField("Observaciones", validators=[DataRequired(), Length(max=4092)])
    sentencia_url = StringField("V.P. Sentencia URL", validators=[DataRequired(), Length(max=512), Regexp(URL_REGEXP)])
    guardar = SubmitField("Guardar")


class REPSVASearchForm(FlaskForm):
    """Formulario para buscar REPSVMAgresor"""

    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    numero_causa = StringField("Numero de causa", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
