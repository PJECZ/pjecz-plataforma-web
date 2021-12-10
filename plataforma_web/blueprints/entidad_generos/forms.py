"""
Entidad Generos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.fields.core import DateField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.entidad_generos.models import EntidadGenero


class EntidadGeneroForm(FlaskForm):
    """Formulario EntidadGenero"""

    nombre_anterior = StringField("Nombre Anterior", validators=[DataRequired(), Length(max=256)])
    nombre_actual = StringField("Nombre Actual", validators=[DataRequired(), Length(max=256)])
    fecha_nacimiento = DateField("Fecha de Nacimiento", validators=[Optional()])
    lugar_nacimiento = StringField("Lugar de Nacimiento", validators=[Optional()])
    genero_anterior = SelectField("Género Anterior", choices=EntidadGenero.GENEROS, validators=[DataRequired()])
    genero_actual = SelectField("Género Actual", choices=EntidadGenero.GENEROS, validators=[DataRequired()])
    num_empleado = StringField("Número de Empleado", validators=[Optional()])
    nombre_padre = StringField("Nombre del Padre", validators=[Length(max=256)])
    nombre_madre = StringField("Nombre de la Madre", validators=[Length(max=256)])
    procedimiento = StringField("Procedimiento", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
