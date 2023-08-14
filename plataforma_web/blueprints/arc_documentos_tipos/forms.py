"""
Archivo Documentos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ArcDocumentoTipoForm(FlaskForm):
    """Formulario Documento Tipo"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=32)])
    guardar = SubmitField("Guardar")
