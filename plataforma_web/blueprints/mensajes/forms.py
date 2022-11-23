"""
Mensaje, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class MensajeConversacionNewForm(FlaskForm):
    """Formulario Mensaje"""

    autor = StringField("Autor", validators=[DataRequired(), Length(max=128)])
    destinatario = SelectField("Destinatario", coerce=int, validate_choice=False, validators=[DataRequired()])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired(), Length(max=512)])
    crear = SubmitField("Crear")


class MensajeRespuestaForm(FlaskForm):
    """Respueta a un Mensaje"""

    asunto = StringField("Asunto", validators=[DataRequired(), Length(max=128)])
    respuesta = TextAreaField("Respuesta", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Envíar")
