"""
Inventarios Modelos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class InvModeloForm(FlaskForm):
    """Formulario InvModelo"""

    nombre = StringField("Marca", validators=[DataRequired()])  # solo lectrua
    descripcion = StringField("Descripción del modelo", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
