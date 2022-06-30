"""
Financieros Vales, formularios
"""
from flask_wtf import FlaskForm
from wtforms import FloatField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.fin_vales.models import FinVale


class FinValeForm(FlaskForm):
    """Formulario FinVale"""

    usuario_nombre = StringField("Usted es")  # Read only
    tipo = SelectField("Tipo", choices=FinVale.TIPOS, validators=[DataRequired()])
    justificacion = TextAreaField("Justificación", validators=[DataRequired(), Length(max=1024)])
    monto = FloatField("Monto", validators=[DataRequired()])
    solicito_nombre = StringField("Quien solicita", validators=[DataRequired(), Length(max=256)])
    solicito_puesto = StringField("Puesto de quien solicita", validators=[DataRequired(), Length(max=256)])
    solicito_email = StringField("e-mail de quien solicita", validators=[DataRequired(), Length(max=256)])
    autorizo_nombre = StringField("Quien autoriza", validators=[DataRequired(), Length(max=256)])
    autorizo_puesto = StringField("Puesto de quien autoriza", validators=[DataRequired(), Length(max=256)])
    autorizo_email = StringField("e-mail de quien autoriza", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class FinValeRequestTaskForm(FlaskForm):
    """Formulario para solicitar un vale"""

    solicito_nombre = StringField("Usted es quien solicita")  # Read only
    usuario_nombre = StringField("Elaborado por")  # Read only
    tipo = StringField("Tipo")  # Read only
    justificacion = TextAreaField("Justificación")  # Read only
    monto = FloatField("Monto")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica (CUIDADO: Si es incorrecta será cancelado)", validators=[DataRequired(), Length(6, 64)])
    solicitar = SubmitField("Solicitar")


class FinValeAuthorizeTaskForm(FlaskForm):
    """Formulario para autorizar un vale"""

    autorizo_nombre = StringField("Usted es quien autoriza")  # Read only
    solicito_nombre = StringField("Quien solicita")  # Read only
    usuario_nombre = StringField("Elaborado por")  # Read only
    tipo = StringField("Tipo")  # Read only
    justificacion = TextAreaField("Justificación")  # Read only
    monto = FloatField("Monto")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica (CUIDADO: Si es incorrecta será cancelado)", validators=[DataRequired(), Length(6, 64)])
    autorizar = SubmitField("Autorizar")
