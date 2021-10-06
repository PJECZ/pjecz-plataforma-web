"""
Modulos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ModuloForm(FlaskForm):
    """Formulario Modulo"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    nombre_corto = StringField("Nombre para menú", validators=[DataRequired(), Length(max=64)])
    icono = StringField("Icono", validators=[DataRequired(), Length(max=48)], default="mdi:folder")
    ruta = StringField("Ruta (comienza con /)", validators=[DataRequired(), Length(max=64)], default="/")
    en_navegacion = BooleanField("En navegación", validators=[Optional()], default=True)
    guardar = SubmitField("Guardar")
