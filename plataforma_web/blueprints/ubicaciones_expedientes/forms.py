"""
Ubicacines de Expedientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente


class UbicacionExpedienteNewForm(FlaskForm):
    """ Formulario para nuevo Ubicación de Expediente """

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=256)])
    ubicacion = SelectField("Ubicación", validators=[DataRequired()], choices=UbicacionExpediente.UBICACIONES)
    guardar = SubmitField("Guardar")


class UbicacionExpedienteEditForm(FlaskForm):
    """ Formulario para editar Ubicación de Expediente """

    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=256)])
    ubicacion = SelectField("Ubicación", validators=[DataRequired()], choices=UbicacionExpediente.UBICACIONES)
    guardar = SubmitField("Guardar")
