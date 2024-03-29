"""
Inventarios Equipos Fotos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class InvEquipoFotoNewForm(FlaskForm):
    """Formulario para subir archivos"""

    inv_equipo = StringField("Equipo")  # read only
    descripcion = StringField("Descripción del archivo", validators=[DataRequired(), Length(max=512)])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Subir Archivo")
