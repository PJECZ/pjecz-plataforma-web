"""
Ubicacines de Expedientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente


class UbicacionExpedienteForm(FlaskForm):
    """ Formulario Ubicación de Expediente """

    expediente = StringField("Expediente", validators=[DataRequired(), Length(max=256)])
    ubicacion = SelectField("Ubicación", validators=[DataRequired()], choices=UbicacionExpediente.UBICACIONES)
    guardar = SubmitField("Guardar")
