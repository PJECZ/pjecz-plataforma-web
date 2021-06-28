"""
Edictos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

EXPEDIENTE_REGEXP = r"^\d+/[12]\d\d\d$"
NUMERO_PUBLICACION_REGEXP = r"^\d+/[12]\d\d\d$"


class EdictoNewForm(FlaskForm):
    """Formulario para nuevo Edicto"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripcion", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    numero_publicacion = StringField("No. de publicación (número/año)", validators=[Optional(), Length(max=16), Regexp(NUMERO_PUBLICACION_REGEXP)])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class EdictoEditForm(FlaskForm):
    """Formulario para editar Edicto"""

    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripcion", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    numero_publicacion = StringField("No. de publicación (número/año)", validators=[Optional(), Length(max=16), Regexp(NUMERO_PUBLICACION_REGEXP)])
    guardar = SubmitField("Guardar")


class EdictoSearchForm(FlaskForm):
    """Formulario para buscar Edictos"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    descripcion = StringField("Descripcion", validators=[Optional(), Length(max=256)])
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    numero_publicacion = StringField("No. de publicación (número/año)", validators=[Optional(), Length(max=16), Regexp(NUMERO_PUBLICACION_REGEXP)])
    buscar = SubmitField("Buscar")
