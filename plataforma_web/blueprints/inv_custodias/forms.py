"""
Custodias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional


class InvCustodiaForm(FlaskForm):
    """Formulario InvCustodia"""

    usuario = StringField("Usuario")
    oficina = StringField("Oficina")
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
