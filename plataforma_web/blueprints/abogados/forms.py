"""
Abogados, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AbogadoForm(FlaskForm):
    """ Formulario Abogado """

    numero = StringField("Número", validators=[DataRequired()])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    libro = StringField("Libro", validators=[DataRequired(), Length(max=256)])
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class AbogadoSearchForm(FlaskForm):
    """ Formulario para buscar Abogados """

    nombre = StringField("Nombre", validators=[Optional(), Length(max=64)])
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")
