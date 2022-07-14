"""
Inventarios Custodias, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Optional


class InvCustodiaForm(FlaskForm):
    """Formulario InvCustodia"""

    usuario = StringField("Usuario")
    oficina = StringField("Oficina")
    fecha = DateField("Fecha", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class InvCustodiaSearchForm(FlaskForm):
    """Formulario buscar InvCustodia"""

    id = IntegerField("ID", validators=[Optional()])
    nombre_completo = StringField("Nombre Completo", validators=[Optional()])
    fecha_desde = DateField("Fecha desde", validators=[Optional()])
    fecha_hasta = DateField("Fecha hasta", validators=[Optional()])
    buscar = SubmitField("Buscar")
