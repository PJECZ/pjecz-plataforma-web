"""
Custodias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

# from plataforma_web.blueprints.usuarios.models import Usuario


# def oficinas_opciones():
#     """Oficinas: opciones para select"""
#     return Oficina.query.filter_by(estatus="A").order_by(Oficina.clave)


# def usuarios_opciones():
#     """Oficinas: opciones para select"""
#     return Usuario.query.filter_by(estatus="A").order_by(Usuario.nombres)


class INVCustodiaForm(FlaskForm):
    """Formulario INVCustodia"""

    usuario = StringField("Usuario")
    # usuario = QuerySelectField(label="Nombre Custodia", query_factory=usuarios_opciones, get_label="nombre", validators=[DataRequired()])
    oficina = StringField("Oficina")
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
