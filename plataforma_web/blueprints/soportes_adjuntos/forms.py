"""
Soportes Tickets, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.funcionarios.models import Funcionario


class SoporteAdjuntoNewForm(FlaskForm):
    """Formulario para subir archivos"""

    usuario = StringField("Usuario")  # Read only
    problema = TextAreaField("Descripción del problema")  # Read only
    categoria = StringField("Categoría")  # Read only
    descripcion = StringField("Descripción del archivo", validators=[DataRequired(), Length(max=512)])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Subir Archivo")
