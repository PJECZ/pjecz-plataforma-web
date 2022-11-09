"""
Oficinas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, RadioField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.domicilios.models import Domicilio
from plataforma_web.blueprints.oficinas.models import Oficina


def distritos_opciones():
    """Distrito: opciones para select"""
    return Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()


def domicilios_opciones():
    """Domicilio: opciones para select"""
    return Domicilio.query.filter_by(estatus="A").order_by(Domicilio.edificio).all()


class OficinaForm(FlaskForm):
    """Formulario Oficina"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=32)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    descripcion_corta = StringField("Descripción Corta", validators=[DataRequired(), Length(max=64)])
    distrito = QuerySelectField("Distrito", query_factory=distritos_opciones, get_label="nombre", validators=[DataRequired()])
    domicilio = QuerySelectField("Domicilio", query_factory=domicilios_opciones, get_label="edificio", validators=[DataRequired()])
    apertura = TimeField("Horario de apertura", validators=[DataRequired()], format="%H:%M")
    cierre = TimeField("Horario de cierre", validators=[DataRequired()], format="%H:%M")
    limite_personas = IntegerField("Límite de personas", validators=[DataRequired()])
    tipo = RadioField("Tipo", choices=Oficina.TIPOS, default="NO DEFINIDO", validators=[DataRequired()])
    es_jurisdiccional = BooleanField("Es Jurisdiccional", validators=[Optional()])
    guardar = SubmitField("Guardar")


class OficinaSearchForm(FlaskForm):
    """Buscar Oficinas"""

    clave = StringField("Clave", validators=[Optional(), Length(max=32)])
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=512)])
    buscar = SubmitField("Buscar")
