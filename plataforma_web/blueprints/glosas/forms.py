"""
Glosas, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP
from plataforma_web.blueprints.glosas.models import Glosa


class GlosaNewForm(FlaskForm):
    """Formulario para nueva Glosa"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha = DateField("Fecha", validators=[DataRequired()])
    tipo_juicio = SelectField("Tipo de juicio", choices=Glosa.TIPOS_JUICIOS)
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=64)])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class GlosaEditForm(FlaskForm):
    """Formulario para editar Glosa"""

    fecha = DateField("Fecha", validators=[DataRequired()])
    tipo_juicio = SelectField("Tipo de juicio", choices=Glosa.TIPOS_JUICIOS)
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=64)])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    guardar = SubmitField("Guardar")


class GlosaSearchForm(FlaskForm):
    """Formulario para buscar Glosas"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    tipo_juicio = SelectField("Tipo de juicio", choices=Glosa.TIPOS_JUICIOS)
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=64)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    buscar = SubmitField("Buscar")


class GlosaSearchAdminForm(FlaskForm):
    """Formulario para buscar Glosas"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    tipo_juicio = SelectField("Tipo de juicio", choices=Glosa.TIPOS_JUICIOS)
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=64)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    buscar = SubmitField("Buscar")
