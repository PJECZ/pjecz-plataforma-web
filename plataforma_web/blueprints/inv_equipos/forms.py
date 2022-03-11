"""
Equipos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.inv_modelos.models import InvModelo
from plataforma_web.blueprints.inv_redes.models import InvRedes


def modelos_opciones():
    """Seleccionar la modelo para select"""
    return InvModelo.query.filter_by(estatus="A").order_by(InvModelo.descripcion).all()


def redes_opciones():
    """Seleccionar la modelo para select"""
    return InvRedes.query.filter_by(estatus="A").order_by(InvRedes.nombre).all()


class InvEquipoForm(FlaskForm):
    """Formulario InvEquipo"""

    custodia = StringField("Custodia")
    puesto = StringField("Puesto")
    email = StringField("Email")
    oficina = StringField("Oficina")
    modelo = QuerySelectField(label="Modelo", query_factory=modelos_opciones, get_label="marca_modelo", validators=[DataRequired()])  # solo lectrua
    red = QuerySelectField(label="Red", query_factory=redes_opciones, get_label="nombre", validators=[Optional()])  # solo lectrua
    adquisicion_fecha = DateField("Fecha de adquisición", validators=[Optional()])
    numero_serie = StringField("Número de serie", validators=[Optional()])
    numero_inventario = IntegerField("Número de inventario", validators=[Optional()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    direccion_ip = StringField("Dirección IP", validators=[Optional()])
    direccion_mac = StringField("Dirección MAC", validators=[Optional()])
    numero_nodo = IntegerField("Número de nodo", validators=[Optional()])
    numero_switch = IntegerField("Número de switch", validators=[Optional()])
    numero_puerto = IntegerField("Número de puerto", validators=[Optional()])
    guardar = SubmitField("Guardar")
