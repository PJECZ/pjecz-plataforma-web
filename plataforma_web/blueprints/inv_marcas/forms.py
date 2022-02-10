"""
Marcas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class INVMarcaForm(FlaskForm):
    """Formulario INVMarca"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
