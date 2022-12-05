"""
REPSVM Agresores, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from lib.safe_string import URL_REGEXP

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor


def distritos_opciones():
    """Distritos: opciones para select"""
    return Distrito.query.filter_by(estatus="A").filter_by(es_distrito_judicial=True).order_by(Distrito.nombre).all()


class REPSVMAgresorForm(FlaskForm):
    """Formulario REPSVMAgresor"""

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre", validators=[DataRequired()])
    delito_generico = StringField("Delito genérico", validators=[DataRequired(), Length(max=256)])
    delito_especifico = TextAreaField("Delito específico", validators=[DataRequired(), Length(max=1024)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    numero_causa = StringField("Numero de causa", validators=[DataRequired(), Length(max=256)])
    pena_impuesta = StringField("Pena impuesta", validators=[DataRequired(), Length(max=256)])
    tipo_juzgado = SelectField("Tipo de juzgado", choices=REPSVMAgresor.TIPOS_JUZGADOS, validators=[DataRequired()])
    tipo_sentencia = SelectField("Tipo de sentencia", choices=REPSVMAgresor.TIPOS_SENTENCIAS, validators=[DataRequired()])
    sentencia_url = StringField("V.P. Sentencia URL", validators=[Optional(), Length(max=512), Regexp(URL_REGEXP)])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=4092)])
    guardar = SubmitField("Guardar")


class REPSVASearchForm(FlaskForm):
    """Formulario para buscar REPSVMAgresor"""

    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    numero_causa = StringField("Numero de causa", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
