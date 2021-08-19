"""
Listas de Acuerdos Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP, FOLIO_REGEXP


class ListaDeAcuerdoAcuerdoForm(FlaskForm):
    """Formulario acuerdos"""

    folio = StringField("Folio", validators=[Optional(), Length(max=16), Regexp(FOLIO_REGEXP)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actor = StringField("Actor", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado", validators=[DataRequired(), Length(max=256)])
    tipo_acuerdo = StringField("Tipo de acuerdo", validators=[DataRequired(), Length(max=256)])
    tipo_juicio = StringField("Tipo de juicio", validators=[DataRequired(), Length(max=256)])
    referencia = IntegerField("Referencia", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class ListaDeAcuerdoAcuerdoSearchForm(FlaskForm):
    """Formulario para buscar acuerdos"""

    folio = StringField("Folio", validators=[Optional(), Length(max=16), Regexp(FOLIO_REGEXP)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    actor = StringField("Actor", validators=[Optional(), Length(max=256)])
    demandado = StringField("Demandado", validators=[Optional(), Length(max=256)])
    tipo_acuerdo = StringField("Tipo de acuerdo", validators=[Optional(), Length(max=256)])
    tipo_juicio = StringField("Tipo de juicio", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
