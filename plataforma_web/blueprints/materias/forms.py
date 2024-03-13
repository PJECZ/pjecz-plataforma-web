"""
Materias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class MateriaForm(FlaskForm):
    """Formulario Materia"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=64)])
    descripcion = TextAreaField("Descripción", validators=[DataRequired(), Length(max=1024)])
    guardar = SubmitField("Guardar")
