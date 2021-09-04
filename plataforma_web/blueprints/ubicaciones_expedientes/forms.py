"""
Ubicacines de Expedientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP
from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente


class UbicacionExpedienteNewForm(FlaskForm):
    """Formulario para nuevo Ubicación de Expediente"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    ubicacion = RadioField("Ubicación", validators=[DataRequired()], choices=UbicacionExpediente.UBICACIONES)
    guardar = SubmitField("Guardar")


class UbicacionExpedienteEditForm(FlaskForm):
    """Formulario para editar Ubicación de Expediente"""

    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    ubicacion = RadioField("Ubicación", validators=[DataRequired()], choices=UbicacionExpediente.UBICACIONES)
    guardar = SubmitField("Guardar")


class UbicacionExpedienteSearchForm(FlaskForm):
    """Formulario para buscar Ubicación de Expediente"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    buscar = SubmitField("Buscar")


class UbicacionExpedienteSearchAdminForm(FlaskForm):
    """Formulario para buscar Ubicación de Expediente"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    expediente = StringField("Expediente", validators=[Optional(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    ubicacion = RadioField("Ubicación", validators=[Optional()], choices=UbicacionExpediente.UBICACIONES)
    buscar = SubmitField("Buscar")
