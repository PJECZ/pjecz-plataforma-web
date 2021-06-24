"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class CIDProcedimientoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    contenido = HiddenField("Contenido", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")
