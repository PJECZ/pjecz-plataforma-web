"""
Transcripciones, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TranscripcionNewForm(FlaskForm):
    """ Formulario Transcripcion """

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=24)])
    audio = FileField("Archivo de audio FLAC", validators=[FileRequired()])
    guardar = SubmitField("Transcribir")


class TranscripcionEditForm(FlaskForm):
    """ Formulario Transcripcion """

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=24)])
    guardar = SubmitField("Guardar")
