"""
CID Registros, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.cid_formatos.models import CIDFormato


def formatos_opciones():
    """ Formatos: opciones para select """
    return CIDFormato.query.filter(CIDFormato.estatus == "A").order_by(CIDFormato.descripcion).limit(100).all()


class CIDRegistroForm(FlaskForm):
    """ Formulario CID Registro """

    formato = QuerySelectField(query_factory=formatos_opciones, get_label="descripcion")
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
