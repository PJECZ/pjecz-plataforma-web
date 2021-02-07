"""
Abogados, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class AbogadoForm(FlaskForm):
    """ Formulario abogado """

    numero = StringField("Número", validators=[DataRequired()])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    libro = StringField("Libro", validators=[DataRequired(), Length(max=256)])
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
