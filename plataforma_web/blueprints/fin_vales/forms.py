"""
Financieros Vales, formularios
"""
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.fin_vales.models import FinVale


class FinValeEditForm(FlaskForm):
    """Formulario para editar un vale"""

    usuario_email = StringField("El vale es para")
    solicito_email = StringField("Quien solicita")
    autorizo_email = StringField("Quien autoriza (Recursos Financieros)")
    tipo = SelectField("Tipo", choices=FinVale.TIPOS, validators=[DataRequired()])
    justificacion = TextAreaField("Justificación", validators=[DataRequired(), Length(max=1024)])
    monto = FloatField("Monto", validators=[DataRequired()])
    actualizar = SubmitField("Actualizar")


class FinValeStep1CreateForm(FlaskForm):
    """Formulario Vale (step 1 create) Crear"""

    usuario_nombre = StringField("Usted es")  # Read only
    usuario_puesto = StringField("Su puesto")  # Read only
    usuario_email = StringField("Su e-mail")  # Read only
    tipo = SelectField("Tipo", choices=FinVale.TIPOS, validators=[DataRequired()])
    justificacion = TextAreaField("Justificación", validators=[DataRequired(), Length(max=1024)])
    monto = FloatField("Monto", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class FinValeStep2RequestForm(FlaskForm):
    """Formulario Vale (step 2 request) Solicitar"""

    solicito_nombre = StringField("Usted es")  # Read only
    solicito_puesto = StringField("Su puesto")  # Read only
    solicito_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    solicitar = SubmitField("Solicitar")


class FinValeCancel2RequestForm(FlaskForm):
    """Formulario Vale (cancel 2 request) Cancelar solicitado"""

    solicito_nombre = StringField("Usted es")  # Read only
    solicito_puesto = StringField("Su puesto")  # Read only
    solicito_email = StringField("Su e-mail")  # Read only
    motivo = StringField("Motivo", validators=[DataRequired(), Length(max=256)])
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    cancelar = SubmitField("Cancelar")


class FinValeStep3AuthorizeForm(FlaskForm):
    """Formulario Vale (step 3 authorize) Autorizar"""

    autorizo_nombre = StringField("Usted es")  # Read only
    autorizo_puesto = StringField("Su puesto")  # Read only
    autorizo_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    autorizar = SubmitField("Autorizar")


class FinValeCancel3AuthorizeForm(FlaskForm):
    """Formulario Vale (cancel 3 authorize) Cancelar autorizado"""

    autorizo_nombre = StringField("Usted es")  # Read only
    autorizo_puesto = StringField("Su puesto")  # Read only
    autorizo_email = StringField("Su e-mail")  # Read only
    motivo = StringField("Motivo", validators=[DataRequired(), Length(max=256)])
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    cancelar = SubmitField("Cancelar")


class FinValeStep4DeliverForm(FlaskForm):
    """Formulario Vale (step 4 deliver) Entregar"""

    folio = StringField("Folio", validators=[DataRequired(), Length(max=64)])
    entregar = SubmitField("Entregar")


class FinValeStep5AttachmentsForm(FlaskForm):
    """Formulario Vale (step 5 attachments) Adjuntar"""

    vehiculo_descripcion = StringField("Descripción del vehículo", validators=[DataRequired(), Length(max=256)])
    tanque_inicial = StringField("Tanque inicial", validators=[Optional(), Length(max=48)])
    tanque_final = StringField("Tanque final", validators=[Optional(), Length(max=48)])
    kilometraje_inicial = IntegerField("Kilometraje inicial", validators=[Optional()])
    kilometraje_final = IntegerField("Kilometraje final", validators=[Optional()])
    concluir = SubmitField("Concluir entrega de adjuntos")


class FinValeStep6ArchiveForm(FlaskForm):
    """Formulario Vale (step 6 archive) Archivar"""

    notas = TextAreaField("Notas", validators=[DataRequired(), Length(max=1024)])
    archivar = SubmitField("Archivar")
