"""
Inventarios Equipos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from lib.safe_string import MAC_ADDRESS_REGEXP

from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.inv_modelos.models import InvModelo
from plataforma_web.blueprints.inv_redes.models import InvRed


def inv_modelos_opciones():
    """Seleccionar la modelo para select"""
    return InvModelo.query.filter_by(estatus="A").order_by(InvModelo.descripcion).all()


def inv_redes_opciones():
    """Seleccionar la modelo para select"""
    return InvRed.query.filter_by(estatus="A").order_by(InvRed.nombre).all()


class InvEquipoForm(FlaskForm):
    """Formulario InvEquipo"""

    custodia = StringField("Custodia")  # Read only
    puesto = StringField("Puesto")  # Read only
    email = StringField("Email")  # Read only
    oficina = StringField("Oficina")  # Read only
    inv_modelo = QuerySelectField(label="Modelo", query_factory=inv_modelos_opciones, get_label="marca_modelo", validators=[DataRequired()])
    inv_red = QuerySelectField(label="Red", query_factory=inv_redes_opciones, get_label="nombre", validators=[DataRequired()])
    fecha_fabricacion = DateField("Fecha de fabricación", validators=[Optional()])
    numero_serie = StringField("Número de serie", validators=[Optional()])
    numero_inventario = IntegerField("Número de inventario", validators=[Optional()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    tipo = RadioField("Tipo de equipo", choices=InvEquipo.TIPOS, default="OTRO", validators=[DataRequired()])
    direccion_ip = StringField("Dirección IP", validators=[Optional()])
    direccion_mac = StringField("Dirección MAC", validators=[Optional(), Regexp(MAC_ADDRESS_REGEXP)])
    numero_nodo = IntegerField("Número de nodo", validators=[Optional()])
    numero_switch = IntegerField("Número de switch", validators=[Optional()])
    numero_puerto = IntegerField("Número de puerto", validators=[Optional()])
    guardar = SubmitField("Guardar")


class InvEquipoSearchForm(FlaskForm):
    """Formulario Buscar Equipos"""

    descripcion = StringField("Descripción", validators=[Optional(), Length(max=256)])
    numero_serie = StringField("Número de serie", validators=[Optional()])
    numero_inventario = IntegerField("Número de inventario", validators=[Optional()])
    tipo = StringField("Tipo de equipo", validators=[Optional()])
    direccion_mac = StringField("Dirección mac", validators=[Optional()])
    direccion_ip = StringField("Dirección ip", validators=[Optional()])
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")


class InvEquipoChangeCustodia(FlaskForm):
    """Formulario para cambiar la custodia de los equipos"""

    inv_custodia = SelectField(label="Custodia", coerce=str, validators=[DataRequired()], validate_choice=False)
    guardar = SubmitField("Transferir")
