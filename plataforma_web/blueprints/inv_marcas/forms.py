"""
Marcas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class INVMarcasForm(FlaskForm):
    """Formulario INVMarcas"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
