"""
Tesis-sentencias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.sentencias.models import Sentencia
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia


def sentencias_opciones():
    """Sentencias: opciones para select"""
    return Sentencia.query.filter_by(estatus="A").order_by(Sentencia.sentencia).all()


def tesis_opciones():
    """Tesis y jursprudencias: opciones para select"""
    return TesisJurisprudencia.query.filter_by(estatus="A").order_by(TesisJurisprudencia.clave_control).all()


class TesisSentenciasForm(FlaskForm):
    """Formulario TesisSentencias"""

    sentencia = QuerySelectField(query_factory=sentencias_opciones, get_label="sentencia", validators=[DataRequired()])
    tesis = QuerySelectField(query_factory=tesis_opciones, get_label="clave_control", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class TesisSentenciaWithSentenciaForm(FlaskForm):
    """Formulario TesisSentencia"""

    sentencia = StringField("Sentencia")  # Solo lectura
    tesis = QuerySelectField(query_factory=tesis_opciones, get_label="clave_control", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class TesisSentenciaWithTesisForm(FlaskForm):
    """Formulario TesisSentencia"""
    sentencia = QuerySelectField(query_factory=sentencias_opciones, get_label="sentencia", validators=[DataRequired()])
    tesis = StringField("Tesis")  # Solo lectura
    guardar = SubmitField("Guardar")
