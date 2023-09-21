"""
Estadisticas Variables, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

CLAVE_REGEXP = r"^S\wT\d\w[\w\d]\d{6}$"


class EstVariableForm(FlaskForm):
    """Formulario EstVariable"""

    clave = StringField("Clave SxTnMz000000", validators=[DataRequired(), Length(max=16), Regexp(CLAVE_REGEXP)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
