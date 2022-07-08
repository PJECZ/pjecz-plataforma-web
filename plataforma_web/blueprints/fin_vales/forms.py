"""
Financieros Vales, formularios
"""
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.fin_vales.models import FinVale


class FinValeStep1PendingForm(FlaskForm):
    """Formulario Vale PASO 1 PENDIENTE"""

    usuario_nombre = StringField("Usted es")  # Read only
    usuario_puesto = StringField("Su puesto")  # Read only
    usuario_email = StringField("Su e-mail")  # Read only
    tipo = SelectField("Tipo", choices=FinVale.TIPOS, validators=[DataRequired()])
    justificacion = TextAreaField("Justificación", validators=[DataRequired(), Length(max=1024)])
    monto = FloatField("Monto", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class FinValeStep2RequestForm(FlaskForm):
    """Formulario Vale PASO 2 SOLICITADO"""

    solicito_nombre = StringField("Usted es")  # Read only
    solicito_puesto = StringField("Su puesto")  # Read only
    solicito_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    solicitar = SubmitField("Solicitar")


class FinValeCancel2RequestForm(FlaskForm):
    """Formulario Vale CANCELAR 2 SOLICITADO"""

    solicito_nombre = StringField("Usted es")  # Read only
    solicito_puesto = StringField("Su puesto")  # Read only
    solicito_email = StringField("Su e-mail")  # Read only
    motivo = StringField("Motivo", validators=[DataRequired(), Length(max=256)])
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    cancelar = SubmitField("Cancelar")


class FinValeStep3AuthorizeForm(FlaskForm):
    """Formulario Vale PASO 3 AUTORIZADO"""

    autorizo_nombre = StringField("Usted es")  # Read only
    autorizo_puesto = StringField("Su puesto")  # Read only
    autorizo_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    autorizar = SubmitField("Autorizar")


class FinValeCancel3AuthorizeForm(FlaskForm):
    """Formulario Vale CANCELAR 3 AUTORIZADO"""

    autorizo_nombre = StringField("Usted es")  # Read only
    autorizo_puesto = StringField("Su puesto")  # Read only
    autorizo_email = StringField("Su e-mail")  # Read only
    motivo = StringField("Motivo", validators=[DataRequired(), Length(max=256)])
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    cancelar = SubmitField("Cancelar")


class FinValeStep4DeliverForm(FlaskForm):
    """Formulario Vale PASO 4 ENTREGADO"""

    folio = StringField("Folio", validators=[DataRequired(), Length(max=64)])
    entregar = SubmitField("Entregar")


class FinValeStep5AttachmentsForm(FlaskForm):
    """Formulario Vale PASO 5 POR REVISAR"""

    vehiculo_descripcion = StringField("Descripción del vehículo", validators=[DataRequired(), Length(max=256)])
    tanque_inicial = StringField("Tanque inicial", validators=[Optional(), Length(max=48)])
    tanque_final = StringField("Tanque final", validators=[Optional(), Length(max=48)])
    kilometraje_inicial = IntegerField("Kilometraje inicial", validators=[Optional()])
    kilometraje_final = IntegerField("Kilometraje final", validators=[Optional()])
    concluir = SubmitField("Concluir entrega de adjuntos")


class FinValeStep6ArchiveForm(FlaskForm):
    """Formulario Vale PASO 6 ARCHIVADO"""

    notas = TextAreaField("Notas", validators=[DataRequired(), Length(max=1024)])
    archivar = SubmitField("Archivar")
