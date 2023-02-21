"""
Archivo Documentos Solicitudes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud


class ArcSolicitudNewForm(FlaskForm):
    """Formulario nueva Solicitud"""

    num_expediente = StringField("Núm. Expediente")
    anio = IntegerField("Año")
    actor = StringField("Actor")
    demandado = StringField("Demandado")
    juicio = StringField("Juicio")
    juzgado_origen = StringField("Juzgado Origen")
    tipo = StringField("Tipo de Documento")
    ubicacion = StringField("Ubicación")
    tipo_juzgado = StringField("Tipo de Juzgado")
    fojas_actuales = IntegerField("Fojas")
    # Campos opcionales para la bitácora o historial
    num_folio = StringField("Núm. de Folio", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    solicitar = SubmitField("Solicitar")


class ArcSolicitudAsignationForm(FlaskForm):
    """Formulario Asignación"""

    asignado = SelectField("Archivista", coerce=int, validate_choice=False, validators=[Optional()])
    asignar = SubmitField("Asignar")


class ArcSolicitudFoundForm(FlaskForm):
    """Formulario Asignación"""

    fojas = IntegerField("Fojas", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    encontrado = SubmitField("Encontrado")
    # Formulario de No Encontrado
    razon = SelectField("Razón", choices=ArcSolicitud.RAZONES, validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    no_encontrado = SubmitField("NO Encontrado")
