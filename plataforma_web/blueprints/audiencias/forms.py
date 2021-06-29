"""
Audiencias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from plataforma_web.blueprints.audiencias.models import Audiencia

EXPEDIENTE_REGEXP = r"^\d+/[12]\d\d\d$"


class AudienciaGenericaForm(FlaskForm):
    """Formulario Audiencia: Civil Familiar Mercantil Letrado TCyA"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M", validators=[DataRequired()])
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actores = StringField("Actores", validators=[Optional(), Length(max=256)])
    demandados = StringField("Demandados", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AudienciaMapoForm(FlaskForm):
    """Formulario Audiencia: Materia Acusatorio Penal Oral"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M", validators=[DataRequired()])
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    sala = StringField("Sala", validators=[Optional(), Length(max=16)])
    caracter = SelectField("Caracter", choices=Audiencia.CARACTERES, validators=[Optional()])
    causa_penal = StringField("Causa penal", validators=[Optional(), Length(max=256)])
    delitos = StringField("Delitos", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AudienciaDipeForm(FlaskForm):
    """Formulario Audiencia: Distritales"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M", validators=[DataRequired()])
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    # Civil, Familiar, Mercantil o Laboral
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actores = StringField("Actores", validators=[Optional(), Length(max=256)])
    demandados = StringField("Demandados", validators=[Optional(), Length(max=256)])
    # Penales
    toca = StringField("Toca", validators=[Optional(), Length(max=64)])
    expediente_origen = StringField("Expediente origen (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    imputados = StringField("Imputados", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AudienciaSapeForm(FlaskForm):
    """Formulario Audiencia: Salas"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    tiempo = DateTimeField("Fecha y hora", format="%Y-%m-%d %H:%M", validators=[DataRequired()])
    tipo_audiencia = StringField("Tipo de audiencia", validators=[DataRequired(), Length(max=64)])
    # Civil, Familiar, Mercantil o Laboral
    expediente = StringField("Expediente (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actores = StringField("Actores", validators=[Optional(), Length(max=256)])
    demandados = StringField("Demandados", validators=[Optional(), Length(max=256)])
    # Penales
    toca = StringField("Toca", validators=[Optional(), Length(max=64)])
    expediente_origen = StringField("Expediente origen (número/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    delitos = StringField("Delitos", validators=[Optional(), Length(max=256)])
    origen = StringField("Origen", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
