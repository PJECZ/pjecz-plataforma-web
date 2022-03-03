"""
INV FOTOS, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class INVEquipoFotoNewForm(FlaskForm):
    """Formulario para subir archivos"""

    equipo = StringField("Equipo")  # read only
    descripcion = StringField("Descripción del archivo", validators=[DataRequired(), Length(max=512)])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Subir Archivo")
