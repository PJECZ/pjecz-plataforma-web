"""
CID Areas Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.cid_areas.models import CIDArea


def cid_area_opciones():
    """CIDArea: opciones para select"""
    return CIDArea.query.filter_by(estatus="A").order_by(CIDArea.nombre).all()


class CIDAreaAutoridadWithAutoridadForm(FlaskForm):
    """Formulario CIDAreaAutoridad con Autoridad"""

    autoridad = StringField("Autoridad")  # Solo lectura
    cid_area = QuerySelectField("Área", query_factory=cid_area_opciones, get_label="nombre", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
