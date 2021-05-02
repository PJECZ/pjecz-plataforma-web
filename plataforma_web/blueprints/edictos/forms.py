"""
Edictos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class EdictoNewForm(FlaskForm):
    """Formulario para nuevo Edicto"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripcion", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=256)])
    numero_publicacion = IntegerField("No. de publicación", validators=[Optional()])
    archivo = FileField("Lista de Acuerdos PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class EdictoEditForm(FlaskForm):
    """Formulario para editar Edicto"""

    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripcion", validators=[DataRequired(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=256)])
    numero_publicacion = IntegerField("No. de publicación", validators=[Optional()])
    guardar = SubmitField("Guardar")


class EdictoSearchForm(FlaskForm):
    """Formulario para buscar Edictos"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=256)])
    expediente = StringField("Expediente", validators=[Optional(), Length(max=256)])
    numero_publicacion = IntegerField("No. de publicación", validators=[Optional()])
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")
