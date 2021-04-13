"""
Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.distritos.models import Distrito


def distritos_opciones():
    """ Distritos: opciones para select """
    return Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()


class AutoridadNewForm(FlaskForm):
    """ Formulario nueva Autoridad """

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Autoridad", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    es_jurisdiccional = BooleanField("Es jurisdiccional", validators=[Optional()])
    guardar = SubmitField("Guardar")


class AutoridadEditForm(FlaskForm):
    """ Formulario modificar Autoridad """

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Autoridad", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    directorio_listas_de_acuerdos = StringField("Directorio listas de acuerdos", validators=[Optional(), Length(max=256)])
    directorio_sentencias = StringField("Directorio listas de acuerdos", validators=[Optional(), Length(max=256)])
    es_jurisdiccional = BooleanField("Es jurisdiccional", validators=[Optional()])
    guardar = SubmitField("Guardar")


class AutoridadSearchForm(FlaskForm):
    """ Formulario para buscar Autoridades """

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    buscar = SubmitField("Buscar")
