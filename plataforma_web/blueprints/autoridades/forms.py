"""
Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional

from plataforma_web.blueprints.distritos.models import Distrito


def distritos_opciones():
    """Distrito: opciones para select"""
    return Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()


class AutoridadForm(FlaskForm):
    """Formulario Autoridad"""

    distrito = QuerySelectField(query_factory=distritos_opciones, get_label="nombre")
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    descripcion_corta = StringField("Descripción corta", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave", validators=[DataRequired(), Length(max=256)])
    es_jurisdiccional = BooleanField("Es Jurisdiccional", validators=[Optional()])
    guardar = SubmitField("Guardar")
