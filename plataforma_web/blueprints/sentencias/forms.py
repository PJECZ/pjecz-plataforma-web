"""
Sentencias, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class SentenciaNewForm(FlaskForm):
    """Formulario para nueva Sentencia"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha = DateField("Fecha", validators=[DataRequired()])
    sentencia = StringField("Sentencia", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=256)])
    es_paridad_genero = BooleanField("Es paridad de género", validators=[Optional()])
    archivo = FileField("Versión Pública de la Sentencia PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class SentenciaEditForm(FlaskForm):
    """Formulario para editar Sentencia"""

    fecha = DateField("Fecha", validators=[DataRequired()])
    sentencia = StringField("Sentencia", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=256)])
    es_paridad_genero = BooleanField("Es paridad de género", validators=[Optional()])
    guardar = SubmitField("Guardar")


class SentenciaSearchForm(FlaskForm):
    """Formulario para buscar Sentencias"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    sentencia = StringField("Sentencia", validators=[Optional(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=256)])
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")
