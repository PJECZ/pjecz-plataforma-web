"""
Sentencias, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio
from plataforma_web.blueprints.sentencias.models import Sentencia

SENTENCIA_REGEXP = r"^\d+/[12]\d\d\d$"
EXPEDIENTE_REGEXP = r"^\d+/[12]\d\d\d$"


def materias_tipos_juicios_opciones():
    """Materias Tipos de Juicios: opciones para select"""
    return MateriaTipoJuicio.query.filter_by(estatus="A").order_by(MateriaTipoJuicio.descripcion).all()


class SentenciaNewForm(FlaskForm):
    """Formulario para nueva Sentencia"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    sentencia = StringField("Sentencia (número/año)", validators=[DataRequired(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    sentencia_fecha = DateField("Fecha de la sentencia", validators=[DataRequired()])
    expediente = StringField("Expediente (número/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha = DateField("Fecha de publicación", validators=[DataRequired()])
    materia = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    materia_tipo_juicio = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    descripcion = StringField("Descripción", validators=[Optional(), Length(256)])
    es_paridad_genero = BooleanField("Es Perspectiva de Género", validators=[Optional()])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class SentenciaEditForm(FlaskForm):
    """Formulario para editar Sentencia"""

    sentencia = StringField("Sentencia (número/año)", validators=[DataRequired(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    sentencia_fecha = DateField("Fecha de la sentencia", validators=[DataRequired()])
    expediente = StringField("Expediente (número/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha = DateField("Fecha de publicación", validators=[DataRequired()])
    materia = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    materia_tipo_juicio = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    descripcion = StringField("Descripción", validators=[Optional(), Length(256)])
    es_paridad_genero = BooleanField("Es Perspectiva de Género", validators=[Optional()])
    guardar = SubmitField("Guardar")


class SentenciaSearchForm(FlaskForm):
    """Formulario para buscar Sentencias"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    sentencia = StringField("Sentencia (número/año)", validators=[Optional(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    # sentencia_fecha
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha_desde = DateField("Fecha de publicación desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha de publicación hasta", validators=[Optional()])
    # materia
    # materia_tipo_juicio
    # descripcion
    # es_paridad_genero
    # tipo_juicio
    buscar = SubmitField("Buscar")


class SentenciaSearchAdminForm(FlaskForm):
    """Formulario para buscar Sentencias"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    sentencia = StringField("Sentencia (número/año)", validators=[Optional(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    # sentencia_fecha
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha_desde = DateField("Fecha de publicación desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha de publicación hasta", validators=[Optional()])
    # materia
    # materia_tipo_juicio
    # descripcion
    # es_paridad_genero
    # tipo_juicio
    buscar = SubmitField("Buscar")
