"""
Domicilios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.distritos.models import Distrito


def distritos_juridiccionales_y_distritales():
    """Opciones para select"""
    return Distrito.query.filter_by(estatus="A").filter_by(es_distrito=True).order_by(Distrito.nombre_corto).all()


class DomicilioForm(FlaskForm):
    """Formulario para Domicilios"""

    edificio = StringField("Edificio", validators=[DataRequired(), Length(max=64)])
    estado = StringField("Estado", validators=[DataRequired(), Length(max=64)])
    municipio = StringField("Municipio", validators=[DataRequired(), Length(max=64)])
    distrito_id = QuerySelectField("Distrito", query_factory=distritos_juridiccionales_y_distritales, get_label="nombre_corto", validators=[DataRequired()])
    calle = StringField("Calle", validators=[DataRequired(), Length(max=256)])
    num_ext = StringField("Núm. Exterior", validators=[Optional()])
    num_int = StringField("Núm. Interior", validators=[Optional()])
    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    cp = IntegerField("CP", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class DomicilioSearchForm(FlaskForm):
    """Formulario para Buscar Domicilios"""

    edificio = StringField("Edificio", validators=[Optional(), Length(max=64)])
    estado = StringField("Estado", validators=[Optional(), Length(max=64)])
    municipio = StringField("Municipio", validators=[Optional(), Length(max=64)])
    calle = StringField("Calle", validators=[Optional(), Length(max=256)])
    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    cp = IntegerField("CP", validators=[Optional()])
    buscar = SubmitField("Buscar")
