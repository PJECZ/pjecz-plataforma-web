"""
Custodias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.oficinas.models import Oficina


# def oficinas_opciones():
#     """Oficinas: opciones para select"""
#     return Oficina.query.filter_by(estatus="A").order_by(Oficina.clave)


class INVCustodiaForm(FlaskForm):
    """Formulario INVCustodia"""

    usuario = StringField("Usuario")
    oficina = StringField("Oficina")
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
