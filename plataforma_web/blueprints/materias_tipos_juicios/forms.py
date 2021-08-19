"""
Materias Tipos de Juicios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.materias.models import Materia


def materias_opciones():
    """Materia: opciones para select"""
    return Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all()


class MateriaTipoJuicioForm(FlaskForm):
    """Formulario MateriaTipoJuicio"""

    materia = QuerySelectField(query_factory=materias_opciones, get_label="nombre")
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
