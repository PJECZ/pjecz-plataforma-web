"""
CID Formatos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class CIDFormatoForm(FlaskForm):
    """Formulario CID Formato"""

    procedimiento_titulo = StringField("Procedimiento")  # Read only
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class CIDFormatoEdit(FlaskForm):
    """Editar Formulario CID Formato"""

    procedimiento_titulo = StringField("Procedimiento")  # Read only
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class CIDFormatoEditAdmin(FlaskForm):
    """Formulario CIDFormatoAdmin"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    procedimiento_titulo = StringField("Procedimiento")  # Read only
    guardar = SubmitField("Guardar")
