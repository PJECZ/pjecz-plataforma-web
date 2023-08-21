"""
Archivo Juzgado Extinto, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ArcJuzgadoExtintoForm(FlaskForm):
    """Formulario ArcJuzgadoExtinto"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    descripcion_corta = StringField("Descripción", validators=[DataRequired(), Length(max=64)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    # distrito =
    guardar = SubmitField("Guardar")
