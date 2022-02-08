"""
Categorias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class INVCategoriaForm(FlaskForm):
    """Formulario INVCategoria"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
