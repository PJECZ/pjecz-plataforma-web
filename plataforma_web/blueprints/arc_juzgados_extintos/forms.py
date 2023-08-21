"""
Archivo Juzgado Extinto, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.distritos.models import Distrito


def distritos_opciones():
    """Opciones para select"""
    return Distrito.query.filter_by(estatus="A").filter_by(es_distrito=True).order_by(Distrito.nombre_corto).all()


class ArcJuzgadoExtintoForm(FlaskForm):
    """Formulario ArcJuzgadoExtinto"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    descripcion_corta = StringField("Descripción", validators=[DataRequired(), Length(max=64)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    distrito = QuerySelectField("Distrito", query_factory=distritos_opciones, get_label="nombre_corto", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
