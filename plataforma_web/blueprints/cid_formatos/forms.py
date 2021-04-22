"""
CID Formatos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento


def procedimientos_opciones():
    """ Procedimientos: opciones para select """
    return CIDProcedimiento.query.filter(CIDProcedimiento.estatus == "A").order_by(CIDProcedimiento.descripcion).limit(100).all()


class CIDFormatoForm(FlaskForm):
    """ Formulario Formato """

    procedimiento = QuerySelectField(query_factory=procedimientos_opciones, get_label="descripcion")
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
