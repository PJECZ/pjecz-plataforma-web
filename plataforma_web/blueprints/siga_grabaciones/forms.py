"""
SIGA Grabaciones, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional


class SIGAGrabacionEditForm(FlaskForm):
    """Formulario para editar Grabación"""

    expediente = StringField("Expediente")
    sala = StringField("Sala")
    inicio = StringField("Inicio")
    nota = TextAreaField("Nota", validators=[Optional(), Length(max=1024)])
    guardar = SubmitField("Guardar")
