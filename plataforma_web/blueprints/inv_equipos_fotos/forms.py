"""
CID Formatos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CIDFormatoForm(FlaskForm):
    """Formulario CID Formato"""

    procedimiento_titulo = StringField("Procedimiento")  # Read only
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")
