"""
Conversacion Escritura, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NotConversacionEscrituraForm(FlaskForm):
    """Formulario NotConversacionEscritura"""

    autor = StringField("Autor", validators=[DataRequired(), Length(max=256)])
    destinatario = StringField("Destinatario", validators=[DataRequired(), Length(max=256)])
    mensjae = TextAreaField("Mensaje", validators=[DataRequired(), Length(max=512)])
    enviar = SubmitField("Envíar")
