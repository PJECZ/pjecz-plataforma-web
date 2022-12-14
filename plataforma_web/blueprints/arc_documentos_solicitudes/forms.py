"""
Archivo Documentos Solicitudes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from plataforma_web.blueprints.arc_documentos_solicitudes.models import ArcDocumentoSolicitud


class ArcDocumentoSolicitudNewForm(FlaskForm):
    """Formulario nueva Solicitud"""

    num_expediente = StringField("Núm. Expediente")
    anio = IntegerField("Año")
    actor = StringField("Actor")
    demandado = StringField("Demandado")
    juicio = StringField("Juicio")
    juzgado_origen = StringField("Juzgado Origen")
    tipo = StringField("Tipo")
    ubicacion = StringField("Ubicación")
    tipo_juzgado = StringField("Tipo de Juzgado")
    # documento_id = HiddenField("Documento id", validators=[DataRequired()])
    fojas = IntegerField("Fojas", validators=[Optional()])
    ultima_observacion = TextAreaField("Última Observación")
    # Campos opcionales para la bitácora o historial
    num_folio = IntegerField("Núm. de Folio", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    solicitar = SubmitField("Solicitar")


class ArcDocumentoSolicitudAsignationForm(FlaskForm):
    """Formulario Asignación"""

    asignado = SelectField("Archivista", coerce=int, validate_choice=False, validators=[Optional()])
    asignar = SubmitField("Asignar")


class ArcDocumentoSolicitudFoundForm(FlaskForm):
    """Formulario Asignación"""

    fojas = IntegerField("Fojas", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    encontrado = SubmitField("Encontrado")
    # Formulario de No Encontrado
    razon = SelectField("Razón", choices=ArcDocumentoSolicitud.RAZONES, validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    no_encontrado = SubmitField("NO Encontrado")


class ArcDocumentoSolicitudSendForm(FlaskForm):
    """Formulario para Enviar"""

    enviar = SubmitField("Enviar")


class ArcDocumentoSolicitudReceiveForm(FlaskForm):
    """Formulario para Recibir"""

    recibir = SubmitField("Recibir")
