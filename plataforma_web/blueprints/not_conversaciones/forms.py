"""
Mensaje, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class NotConversacionNewForm(FlaskForm):
    """Formulario Mensaje"""

    autor = StringField("Autor", validators=[DataRequired(), Length(max=128)])
    destinatario = SelectField("Destinatario", coerce=int, validate_choice=False, validators=[DataRequired()])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired(), Length(max=512)])
    crear = SubmitField("Crear")
