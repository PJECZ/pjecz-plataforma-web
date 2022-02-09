"""
Cit Clientes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional


class CitDiasInhabilesForm(FlaskForm):
    """Formulario CITDíasInhabiles"""

    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=512)])
    guardar = SubmitField("Guardar")
