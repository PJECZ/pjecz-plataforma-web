"""
CITAS Clientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TimeField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


class CITServiciosForm(FlaskForm):
    """Formulario CITDíasInhabiles"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=32)])
    nombre = StringField("Nombre", validators=[Optional(), Length(max=512)])
    solicitar_expedientes = BooleanField("Solicitar Expedientes")
    duracion = TimeField("Duración (horas:minutos)", validators=[DataRequired()], format="%H:%M")

    guardar = SubmitField("Guardar")
