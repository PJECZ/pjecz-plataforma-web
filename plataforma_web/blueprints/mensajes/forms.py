"""
Mensaje, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class MensajeForm(FlaskForm):
    """Formulario Mensaje"""

    autor = StringField("Autor", validators=[DataRequired(), Length(max=256)])
    asunto = StringField("Asunto", validators=[DataRequired(), Length(max=128)])
    contenido = TextAreaField("Contenido", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")


class MensajeRespuestaForm(FlaskForm):
    """Respueta a un Mensaje"""

    autor = StringField("Autor", validators=[DataRequired(), Length(max=256)])
    asunto = StringField("Asunto", validators=[DataRequired(), Length(max=128)])
    respuesta = TextAreaField("Respuesta", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
