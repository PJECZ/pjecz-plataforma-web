"""
Equipos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, IPAddress, MacAddress


class INVEquiposForm(FlaskForm):
    """Formulario InvEquipos"""

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
