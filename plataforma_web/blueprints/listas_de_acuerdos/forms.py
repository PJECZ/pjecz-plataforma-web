"""
Listas de Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.materias.models import Materia


def materias_opciones():
    """Materias: opciones para select"""
    return Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all()


class ListaDeAcuerdoNewForm(FlaskForm):
    """Formulario para nueva Lista de Acuerdo"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha = DateField("Fecha", validators=[DataRequired()])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class ListaDeAcuerdoMateriaNewForm(FlaskForm):
    """Formulario para nueva Lista de Acuerdo de una Materia"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha = DateField("Fecha", validators=[DataRequired()])
    materia = QuerySelectField("Materia", query_factory=materias_opciones, get_label="nombre", validators=[DataRequired()])
    archivo = FileField("Archivo PDF", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class ListaDeAcuerdoEditForm(FlaskForm):
    """Formulario para editar Lista de Acuerdo"""

    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class ListaDeAcuerdoSearchForm(FlaskForm):
    """Formulario para buscar Lista de Acuerdo"""

    distrito = StringField("Distrito")  # Read only
    autoridad = StringField("Autoridad")  # Read only
    fecha_desde = DateField("Fecha desde", validators=[DataRequired()])
    fecha_hasta = DateField("Fecha hasta", validators=[DataRequired()])
    buscar = SubmitField("Buscar")


class ListaDeAcuerdoSearchAdminForm(FlaskForm):
    """Formulario para buscar Lista de Acuerdo"""

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    fecha_desde = DateField("Fecha desde", validators=[DataRequired()])
    fecha_hasta = DateField("Fecha hasta", validators=[DataRequired()])
    buscar = SubmitField("Buscar")
