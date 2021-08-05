"""
Listas de Acuerdos Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

FOLIO_REGEXP = r"^\d+/[12]\d\d\d$"
EXPEDIENTE_REGEXP = r"^\d+/[12]\d\d\d$"


class ListaDeAcuerdoAcuerdoForm(FlaskForm):
    """Formulario ListaDeAcuerdoAcuerdo"""

    folio = StringField("Folio (consecutivo/año)", validators=[Optional(), Length(max=16), Regexp(FOLIO_REGEXP)])
    expediente = StringField("Expediente (consecutivo/año)", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actor = StringField("Actor", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado", validators=[DataRequired(), Length(max=256)])
    tipo_acuerdo = StringField("Tipo de acuerdo", validators=[DataRequired(), Length(max=256)])
    tipo_juicio = StringField("Tipo de juicio", validators=[DataRequired(), Length(max=256)])
    referencia = IntegerField("Referencia", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
