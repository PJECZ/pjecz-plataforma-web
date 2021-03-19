"""
Abogados, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AbogadoForm(FlaskForm):
    """ Formulario Abogado """

    fecha = DateField("Fecha", validators=[DataRequired()])
    numero = StringField("Número", validators=[DataRequired(), Length(max=24)])
    libro = StringField("Libro", validators=[DataRequired(), Length(max=24)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class AbogadoSearchForm(FlaskForm):
    """ Formulario para buscar Abogados """

    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    numero = StringField("Número", validators=[Optional(), Length(max=24)])
    libro = StringField("Libro", validators=[Optional(), Length(max=24)])
    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
