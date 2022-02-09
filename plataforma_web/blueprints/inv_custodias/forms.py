"""
Custodias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.usuarios.models import Usuario


def usuarios_nombres_opciones():
    """Seleccionar correo electronico de usuarios: opciones para select"""
    return Usuario.query.filter_by(estatus="A").order_by(Usuario.nombres).all()


# def usuarios_curp_opciones():
#     """Seleccionar correo electronico de usuarios: opciones para select"""
#     return Usuario.query.filter_by(estatus="A").order_by(Usuario.curp).all()


class INVCustodiaForm(FlaskForm):
    """Formulario INVCustodia"""

    # usuario = StringField("Usuario")  # Read only
    usuario = QuerySelectField(label="Nombres", query_factory=usuarios_nombres_opciones, get_label="nombre", validators=[Optional()])
    # curp_user = QuerySelectField(label="Curp", query_factory=usuarios_curp_opciones, get_label="curp", validators=[Optional()])
    nombre_completo = StringField("Nombre completo", validators=[DataRequired(), Length(max=250)])
    fecha = DateField("Fecha", validators=[DataRequired()])
    curp = StringField("CURP", validators=[DataRequired(), Length(max=50)])
    guardar = SubmitField("Guardar")
