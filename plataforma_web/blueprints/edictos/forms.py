"""
Edictos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class EdictoForm(FlaskForm):
    """ Formulario Edicto """

    descripcion = StringField("Descripcion", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired(), Length(max=256)])
    fecha = DateField("Fecha", validators=[DataRequired()])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=256)])
    numero_publicacion = IntegerField("No. de publicación", validators=[Optional()])
    url = StringField("URL", validators=[Optional()])
    guardar = SubmitField("Guardar")


class EdictoSearchForm(FlaskForm):
    """ Formulario para buscar Edictos """

    descripcion = StringField("Descripcion", validators=[Optional(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
