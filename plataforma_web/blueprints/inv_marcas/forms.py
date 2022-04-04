"""
Inventarios Marcas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class InvMarcaForm(FlaskForm):
    """Formulario InvMarca"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")


class InvMarcaSearchForm(FlaskForm):
    """Formulario buscar InvMarca"""

    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
