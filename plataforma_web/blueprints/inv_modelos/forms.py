"""
Modelos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class INVModelosForm(FlaskForm):
    """Formulario INVModelos"""

    # nombre = StringField("Nombre")  # solo lectrua
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
