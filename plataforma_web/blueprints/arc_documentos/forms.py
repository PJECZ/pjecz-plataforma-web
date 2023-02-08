"""
Archivo Documentos, formularios
"""
from flask_wtf import FlaskForm
from datetime import date
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento


class ArcDocumentoNewForm(FlaskForm):
    """Formulario nuevo Documento"""

    num_expediente = StringField("Núm. Expediente", validators=[DataRequired(), Length(max=16)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1950, date.today().year)])
    juzgado_id = SelectField("Juzgado", coerce=int, validate_choice=False, validators=[DataRequired()])
    actor = StringField("Actor", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado", validators=[DataRequired(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = StringField("Juzgado Origen", validators=[Optional(), Length(max=64)])
    tipo = SelectField("Tipo", choices=ArcDocumento.TIPOS, validators=[DataRequired()])
    ubicacion = SelectField("Ubicación", choices=ArcDocumento.UBICACIONES, validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Juzgado", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class ArcDocumentoEditForm(FlaskForm):
    """Formulario modificar Documento"""

    num_expediente = StringField("Núm. Expediente", validators=[DataRequired(), Length(max=16)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1950, date.today().year)])
    juzgado_id = SelectField("Juzgado", coerce=int, validate_choice=False, validators=[DataRequired()])
    actor = StringField("Actor", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado", validators=[DataRequired(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = StringField("Juzgado Origen", validators=[Optional(), Length(max=64)])
    tipo = SelectField("Tipo", choices=ArcDocumento.TIPOS, validators=[DataRequired()])
    ubicacion = SelectField("Ubicación", choices=ArcDocumento.UBICACIONES, validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Juzgado", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    observaciones = TextAreaField("Motivo", validators=[DataRequired(), Length(min=5, max=256)])
    guardar = SubmitField("Guardar")
