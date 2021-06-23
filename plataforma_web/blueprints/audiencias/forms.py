"""
Audiencias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.audiencias.models import Audiencia


class AudienciaMCFMLDSTForm(FlaskForm):
    """Formulario Audiencia: Materias C F M L Dist. (CyF) Salas (CyF) TCyA"""

    tiempo = DateTimeField("Fecha y hora")
    tipo_audiencia = StringField("Tipo de audiencia")
    expediente = StringField("Expediente")
    actores = StringField("Actores")
    demandados = StringField("Demandados")
    guardar = SubmitField("Guardar")


class AudienciaMAPOForm(FlaskForm):
    """Formulario Audiencia: Materia Acusatorio Penal Oral"""

    tiempo = DateTimeField("Fecha y hora")
    tipo_audiencia = StringField("Tipo de audiencia")
    sala = StringField("Sala")
    caracter = SelectField("Caracter", choices=Audiencia.CARACTERES)
    causa_penal = StringField("Causa penal")
    delitos = StringField("Delitos")
    guardar = SubmitField("Guardar")


class AudienciaDPYSPForm(FlaskForm):
    """Formulario Audiencia: Distritales Penales y Salas Penales"""

    tiempo = DateTimeField("Fecha y hora")
    tipo_audiencia = StringField("Tipo de audiencia")
    toca = StringField("Toca")
    expediente_origen = StringField("Expediente origen")
    delitos = StringField("Delitos")
    imputados = StringField("Imputados")
    guardar = SubmitField("Guardar")
