"""
INV Equipo Foto, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class INVEquipoFotoForm(FlaskForm):
    """Formulario  INVEquipoFoto"""

    equipo = StringField("Equipo")  # Read only
    descripcion = StringField("Descripcion", validators=[DataRequired(), Length(max=512)])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")
