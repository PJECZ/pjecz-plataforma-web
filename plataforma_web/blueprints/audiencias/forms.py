"""
Audiencias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

from plataforma_web.blueprints.audiencias.models import Audiencia

EXPEDIENTE_REGEXP = r"^\d+/[12]\d\d\d$"


class AudienciaGenericaForm(FlaskForm):
    """Formulario Audiencia: Materias Mat. CFML, Dist. CyF, Salas CyF y TCyA"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M")
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    expediente = StringField("Expediente (número/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actores = StringField("Actores", validators=[DataRequired(), Length(max=256)])
    demandados = StringField("Demandados", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AudienciaMapoForm(FlaskForm):
    """Formulario Audiencia: Materia Acusatorio Penal Oral"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M")
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    sala = StringField("Sala", validators=[DataRequired(), Length(max=16)])
    caracter = SelectField("Caracter", choices=Audiencia.CARACTERES, validators=[DataRequired()])
    causa_penal = StringField("Causa penal", validators=[DataRequired(), Length(max=256)])
    delitos = StringField("Delitos", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AudienciaDipesapeForm(FlaskForm):
    """Formulario Audiencia: Distritales Penales y Salas Penales"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M")
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    toca = StringField("Toca", validators=[DataRequired(), Length(max=64)])
    expediente_origen = StringField("Expediente origen (número/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    delitos = StringField("Delitos", validators=[DataRequired(), Length(max=256)])
    imputados = StringField("Imputados", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
