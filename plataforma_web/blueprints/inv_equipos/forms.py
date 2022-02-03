"""
Equipos, formularios
"""
from xmlrpc.client import DateTime
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class INVEquiposForm(FlaskForm):
    """Formulario InvEquipos"""

    adquisicion_fecha = DateField("Fecha de adquisición", validators=[DataRequired()])
    numero_serie = IntegerField("Número de serie", validators=[DataRequired()])
    numero_inventario = IntegerField("Número de inventario", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    direccion_ip = StringField("Dirección IP", validators=[DataRequired(), Length(max=256)])
    direccion_mac = StringField("Dirección MAC", validators=[DataRequired(), Length(max=256)])
    numero_nodo = IntegerField("Número de nodo", validators=[DataRequired()])
    numero_switch = IntegerField("Número de switch", validators=[DataRequired()])
    numero_puerto = IntegerField("Número de puerto", validators=[DataRequired()])
    guardar = SubmitField("Guardar")
