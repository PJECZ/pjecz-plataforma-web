"""
Identidades Generos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.core import DateField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import EXPEDIENTE_REGEXP
from plataforma_web.blueprints.identidades_generos.models import IdentidadGenero


class IdentidadGeneroForm(FlaskForm):
    """Formulario IdentidadGenero"""

    nombre_anterior = StringField("Nombre Anterior", validators=[DataRequired(), Length(max=256)])
    nombre_actual = StringField("Nombre Actual", validators=[DataRequired(), Length(max=256)])
    fecha_nacimiento = DateField("Fecha de Nacimiento", validators=[Optional()])
    lugar_nacimiento = StringField("Lugar de Nacimiento", validators=[Optional()])
    genero_anterior = SelectField("Género Anterior", choices=IdentidadGenero.GENEROS, validators=[DataRequired()])
    genero_actual = SelectField("Género Actual", choices=IdentidadGenero.GENEROS, validators=[DataRequired()])
    nombre_padre = StringField("Nombre del Padre", validators=[Length(max=256)])
    nombre_madre = StringField("Nombre de la Madre", validators=[Length(max=256)])
    procedimiento = StringField("Procedimiento", validators=[DataRequired(), Length(max=256), Regexp(EXPEDIENTE_REGEXP)])
    guardar = SubmitField("Guardar")


class IdentidadGeneroSearchForm(FlaskForm):
    """Formulario para buscar Identidades de Géneros"""

    nombre_actual = StringField("Nombre Actual", validators=[Optional(), Length(max=256)])
    nombre_anterior = StringField("Nombre Anterior", validators=[Optional(), Length(max=256)])
    lugar_nacimiento = StringField("Lugar de Nacimiento", validators=[Optional(), Length(max=256)])
    buscar = SubmitField("Buscar")
