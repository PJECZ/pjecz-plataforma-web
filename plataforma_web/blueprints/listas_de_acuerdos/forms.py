"""
Listas de Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ListaDeAcuerdoNewForm(FlaskForm):
    """ Formulario Lista de Acuerdo """

    distrito = SelectField("Distrito", choices=[])  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=[], validators=[DataRequired()])  # Las opciones se agregan con JS
    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired()])
    url = StringField("URL", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class ListaDeAcuerdoEditForm(FlaskForm):
    """ Formulario Lista de Acuerdo """

    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired()])
    url = StringField("URL", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
