"""
Tesis Jurisprudencias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.epocas.models import Epoca
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia


def epocas_opciones():
    """Epocas: opciones para select"""
    return Epoca.query.filter_by(estatus="A").order_by(Epoca.nombre).all()


def funcionarios_opciones():
    """Funcionarios: opciones para select"""
    return Funcionario.query.filter_by(en_tesis_jurisprudencias=True).filter_by(estatus="A").order_by(Funcionario.nombres).all()


def materias_opciones():
    """Materias: opciones para select"""
    return Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all()


class TesisJurisprudenciaNewForm(FlaskForm):
    """Formulario TesisJurisprudencia"""

    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    subtitulo = StringField("Subtítulo", validators=[Optional(), Length(max=256)])
    tipo = SelectField("Tipo", choices=TesisJurisprudencia.TIPOS, validators=[DataRequired()])
    estado = SelectField("Estatus", choices=TesisJurisprudencia.ESTADOS, validators=[DataRequired()])
    clave_control = StringField("Clave de control", validators=[DataRequired(), Length(max=24)])
    clase = SelectField("Clase", choices=TesisJurisprudencia.CLASES, validators=[DataRequired()])
    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    instancia = StringField("Instancia", validators=[DataRequired(), Length(max=256)])
    materia = QuerySelectField(query_factory=materias_opciones, get_label="nombre", validators=[DataRequired()])
    rubro = StringField("Rubro", validators=[DataRequired(), Length(max=256)])
    texto = TextAreaField("Texto", validators=[DataRequired()])
    precedentes = TextAreaField("Precedentes", validators=[Optional()])
    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label="nombres", validators=[DataRequired()])
    aprobacion_fecha = DateField("Fecha de aprobación", validators=[DataRequired()])
    votacion = StringField("Votación", validators=[Optional(), Length(max=256)])
    votos_particulares = StringField("Votos particulares", validators=[Optional(), Length(max=256)])
    publicacion_tiempo = TimeField("Tiempo de publicación", validators=[DataRequired()])
    aplicacion_tiempo = TimeField("Tiempo de aplicación", validators=[DataRequired()])
    epoca = QuerySelectField(query_factory=epocas_opciones, get_label="nombre")
    guardar = SubmitField("Guardar")


class TesisJurisprudenciaEditForm(FlaskForm):
    """Formulario TesisJurisprudencia"""

    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    subtitulo = StringField("Subtítulo", validators=[Optional(), Length(max=256)])
    tipo = SelectField("Tipo", choices=TesisJurisprudencia.TIPOS, validators=[DataRequired()])
    estado = SelectField("Estatus", choices=TesisJurisprudencia.ESTADOS, validators=[DataRequired()])
    clave_control = StringField("Clave de control", validators=[DataRequired(), Length(max=24)])
    clase = SelectField("Clase", choices=TesisJurisprudencia.CLASES, validators=[DataRequired()])
    instancia = StringField("Instancia", validators=[DataRequired(), Length(max=256)])
    materia = QuerySelectField(query_factory=materias_opciones, get_label="nombre")
    rubro = StringField("Rubro", validators=[DataRequired(), Length(max=256)])
    texto = TextAreaField("Texto", validators=[DataRequired()])
    precedentes = TextAreaField("Precedentes", validators=[Optional()])
    funcionario = QuerySelectField(query_factory=funcionarios_opciones, get_label="nombres")
    aprobacion_fecha = DateField("Fecha de aprobación", validators=[DataRequired()])
    votacion = StringField("Votación", validators=[Optional(), Length(max=256)])
    votos_particulares = StringField("Votos particulares", validators=[Optional(), Length(max=256)])
    publicacion_tiempo = TimeField("Tiempo de publicación", validators=[DataRequired()])
    aplicacion_tiempo = TimeField("Tiempo de aplicación", validators=[DataRequired()])
    epoca = QuerySelectField(query_factory=epocas_opciones, get_label="nombre")
    guardar = SubmitField("Guardar")
