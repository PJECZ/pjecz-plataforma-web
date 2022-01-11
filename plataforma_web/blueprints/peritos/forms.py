"""
Peritos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, Optional

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.peritos.models import Perito
from plataforma_web.blueprints.peritos_tipos.models import PeritoTipo


def distritos_opciones():
    """ Distritos: opciones para select """
    return Distrito.query.filter_by(estatus="A").filter(Distrito.es_distrito_judicial == True).order_by(Distrito.nombre).all()


def peritos_tipos_opciones():
    """ Tipos de Peritos: opciones para select """
    return PeritoTipo.query.filter_by(estatus='A').order_by(PeritoTipo.nombre).all()


class PeritoForm(FlaskForm):
    """ Formulario Perito """

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    perito_tipo = QuerySelectField(query_factory=peritos_tipos_opciones, get_label='nombre')
    domicilio = StringField("Domicilio", validators=[Optional(), Length(max=256)])
    telefono_fijo = StringField("Teléfono fijo", validators=[Optional(), Length(max=256)])
    telefono_celular = StringField("Teléfono celular", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Email()])
    notas = StringField("Notas", validators=[Optional()])
    renovacion = DateField("Renovación", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class PeritoSearchForm(FlaskForm):
    """ Formulario para buscar Peritos """

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre", allow_blank=True)
    nombre = StringField("Nombre", validators=[Optional(), Length(max=256)])
    perito_tipo = QuerySelectField(query_factory=peritos_tipos_opciones, get_label='nombre', allow_blank=True)
    buscar = SubmitField("Buscar")
