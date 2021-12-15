"""
Tesis Jurisprudencias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.epocas.models import Epoca
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia


def epocas_opciones():
    """Epocas: opciones para select"""
    return Epoca.query.filter_by(estatus="A").order_by(Epoca.nombre).all()


def materias_opciones():
    """Materias: opciones para select"""
    return Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all()


class TesisJurisprudenciaForm(FlaskForm):
    """Formulario TesisJurisprudencia"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    subtitulo = StringField("Subtítulo", validators=[Optional(), Length(max=256)])
    tipo = SelectField("Tipo", choices=TesisJurisprudencia.TIPOS, validators=[DataRequired()])
    estado = SelectField("Estatus", choices=TesisJurisprudencia.ESTADOS, validators=[DataRequired()])
    clave_control = StringField("Clave de control", validators=[DataRequired(), Length(max=24)])
    clase = SelectField("Clase", choices=TesisJurisprudencia.CLASES, validators=[DataRequired()])
    materia = QuerySelectField(query_factory=materias_opciones, get_label="nombre", validators=[DataRequired()])
    rubro = StringField("Rubro", validators=[DataRequired(), Length(max=256)])
    texto = TextAreaField("Texto", validators=[DataRequired()])
    precedentes = TextAreaField("Precedentes", validators=[Optional()])
    aprobacion_fecha = DateField("Fecha de aprobación", validators=[DataRequired()])
    votacion = StringField("Votación", validators=[Optional(), Length(max=256)])
    votos_particulares = StringField("Votos particulares", validators=[Optional(), Length(max=256)])
    publicacion_fecha = DateField("Publicación fecha", format="%Y-%m-%d", validators=[DataRequired()])
    publicacion_horas_minutos = TimeField("Publicación hora:minuto", format="%H:%M", validators=[DataRequired()])
    aplicacion_fecha = DateField("Aplicación fecha", format="%Y-%m-%d", validators=[DataRequired()])
    aplicacion_horas_minutos = TimeField("Aplicación hora:minuto", format="%H:%M", validators=[DataRequired()])
    epoca = QuerySelectField(query_factory=epocas_opciones, get_label="nombre")
    guardar = SubmitField("Guardar")
