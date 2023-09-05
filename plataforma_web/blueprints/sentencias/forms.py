"""
Sentencias, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP, SENTENCIA_REGEXP


class SentenciaNewForm(FlaskForm):
    """Formulario para nueva Sentencia"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    sentencia = StringField("Sentencia", validators=[DataRequired(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    sentencia_fecha = DateField("Fecha de la sentencia", validators=[DataRequired()])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha = DateField("Fecha de publicación", validators=[DataRequired()])
    materia = SelectField("Materia", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    materia_tipo_juicio = SelectField("Tipo de Juicio", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=1024)])
    es_perspectiva_genero = BooleanField("Es Perspectiva de Género", validators=[Optional()])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class SentenciaEditForm(FlaskForm):
    """Formulario para editar Sentencia"""

    sentencia = StringField("Sentencia", validators=[DataRequired(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    sentencia_fecha = DateField("Fecha de la sentencia", validators=[DataRequired()])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha = DateField("Fecha de publicación", validators=[DataRequired()])
    materia = SelectField("Materia", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    materia_tipo_juicio = SelectField("Tipo de Juicio", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=1024)])
    es_perspectiva_genero = BooleanField("Es Perspectiva de Género", validators=[Optional()])
    guardar = SubmitField("Guardar")


class SentenciaSearchForm(FlaskForm):
    """Formulario para buscar Sentencias"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    sentencia = StringField("Sentencia", validators=[Optional(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha_desde = DateField("Fecha de publicación desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha de publicación hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")


class SentenciaSearchAdminForm(FlaskForm):
    """Formulario para buscar Sentencias"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    sentencia = StringField("Sentencia", validators=[Optional(), Length(max=16), Regexp(SENTENCIA_REGEXP)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha_desde = DateField("Fecha de publicación desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha de publicación hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")


class SentenciaReportForm(FlaskForm):
    """Formulario para elaborar reporte de listas de acuerdos"""

    autoridad_id = IntegerField("Autoridad ID", validators=[DataRequired()])
    fecha_desde = DateField("Desde", validators=[DataRequired()])
    fecha_hasta = DateField("Hasta", validators=[DataRequired()])
    por_tipos_de_juicios = BooleanField("Por tipos de juicios", validators=[Optional()])
    elaborar = SubmitField("Elaborar")
