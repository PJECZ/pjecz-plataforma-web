"""
REDAM (Registro Estatal de Deudores Alimentarios), formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP


class RedamForm(FlaskForm):
    """Formulario para REDAM"""

    distrito = SelectField("Distrito", validators=[DataRequired()], choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", validators=[DataRequired()], choices=None, validate_choice=False)  # Las opciones se agregan con JS
    nombre = StringField("Nombre del deudor alimentario", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    fecha = DateField("Fecha de emisión de orden de inclusión", validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")


class RedamSearchForm(FlaskForm):
    """Formulario para Buscar en REDAM"""

    nombre = StringField("Nombre del deudor alimentario", validators=[Optional(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    buscar = SubmitField("Buscar")
