"""
Financieros Vales Adjuntos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import FloatField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

from plataforma_web.blueprints.fin_vales_adjuntos.models import FinValeAdjunto


class FinValeAdjuntoForm(FlaskForm):
    """ Formulario FinValeAdjunto """

    fin_vale_usuario_nombre = StringField("Elaborado por")  # Read only
    fin_vale_tipo = StringField("Tipo de vale")  # Read only
    fin_vale_justificacion = TextAreaField("Justificación")  # Read only
    fin_vale_monto = FloatField("Monto")  # Read only
    tipo = SelectField("Tipo de adjunto", choices=FinValeAdjunto.TIPOS, validators=[DataRequired()])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Subir Archivo")
