"""
Equipos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, IPAddress, MacAddress

from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.inv_modelos.models import INVModelo

# from plataforma_web.blueprints.inv_modelos.models import INVMarca
from plataforma_web.blueprints.inv_redes.models import INVRedes


def modelos_opciones():
    """Seleccionar la modelo para select"""
    # return INVModelo.query.join(INVMarca).filter(INVModelo.marca == marca_id).first()
    return INVModelo.query.filter_by(estatus="A").order_by(INVModelo.descripcion).all()


def redes_opciones():
    """Seleccionar la modelo para select"""
    return INVRedes.query.filter_by(estatus="A").order_by(INVRedes.nombre).all()


class INVEquipoForm(FlaskForm):
    """Formulario InvEquipo"""

    custodia = StringField("Custodia")
    modelo = QuerySelectField(label="Modelo", query_factory=modelos_opciones, get_label="descripcion", validators=[DataRequired()])  # solo lectrua
    nombre_red = QuerySelectField(label="Nombre Red", query_factory=redes_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    adquisicion_fecha = DateField("Fecha de adquisición", validators=[DataRequired()])
    numero_serie = IntegerField("Número de serie", validators=[DataRequired()])
    numero_inventario = IntegerField("Número de inventario", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    direccion_ip = StringField("Dirección IP", validators=[IPAddress()])
    direccion_mac = StringField("Dirección MAC", validators=[MacAddress()])
    numero_nodo = IntegerField("Número de nodo", validators=[Optional()])
    numero_switch = IntegerField("Número de switch", validators=[Optional()])
    numero_puerto = IntegerField("Número de puerto", validators=[Optional()])
    guardar = SubmitField("Guardar")
