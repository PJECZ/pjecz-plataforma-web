"""
Financieros Vales, formularios
"""
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.fin_vales.models import FinVale


class FinValeForm(FlaskForm):
    """Formulario FinVale"""

    usuario_nombre = StringField("Elaborado por")  # Read only
    autorizo_nombre = StringField("Quien autoriza", validators=[DataRequired(), Length(max=256)])
    autorizo_puesto = StringField("Puesto de quien autoriza", validators=[DataRequired(), Length(max=256)])
    tipo = SelectField("Tipo", choices=FinVale.TIPOS, validators=[DataRequired()])
    justificacion = TextAreaField("Justificación", validators=[DataRequired(), Length(max=1024)])
    monto = FloatField("Monto", validators=[DataRequired()])
    solicito_nombre = StringField("Quien solicita", validators=[DataRequired(), Length(max=256)])
    solicito_puesto = StringField("Puesto de quien solicita", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
