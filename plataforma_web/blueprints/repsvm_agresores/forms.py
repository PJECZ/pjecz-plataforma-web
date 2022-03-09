"""
REPSVM Agresores, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias_tipos_juzgados.models import MateriaTipoJuzgado
from plataforma_web.blueprints.repsvm_delitos_especificos.models import REPSVMDelitoEspecifico
from plataforma_web.blueprints.repsvm_tipos_sentencias.models import REPSVMTipoSentencia


def distritos_opciones():
    """Distritos: opciones para select"""
    return Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()


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
    materia_tipo_juzgado = QuerySelectField(query_factory=materias_tipos_juzgados_opciones, get_label="descripcion")
    numero_causa = StringField("Numero de causa", validators=[DataRequired(), Length(max=256)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    repsvm_delito_especifico = QuerySelectField(query_factory=repsvm_delitos_especificos_opciones, get_label="descripcion")
    repsvm_tipo_sentencia = QuerySelectField(query_factory=repsvm_tipos_sentencias_opciones, get_label="descripcion")
    pena_impuesta = StringField("Pena impuesta", validators=[DataRequired(), Length(max=256)])
    observaciones = TextAreaField("Pena impuesta", validators=[DataRequired(), Length(max=4092)])
    sentencia_url = StringField("V.P. Sentencia", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
