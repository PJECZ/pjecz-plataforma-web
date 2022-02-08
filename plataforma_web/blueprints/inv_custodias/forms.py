"""
Custodias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional

from wtforms.ext.sqlalchemy.fields import QuerySelectField


# from plataforma_web.blueprints.usuarios.models import Usuario

# from plataforma_web.blueprints.oficinas.models import oficinas


# def usuarios_opciones():
#     """Seleccionar el usuario para select"""
#     return Usuario.query.filter_by(estatus="A").order_by(Usuario.id).all()


# def oficina_opciones():
#     """Seleccionar la oficina para select"""
#     return Oficina.query.filter_by(estatus="A").order_by(Oficina.nombre).all()


class INVCustodiaForm(FlaskForm):
    """Formulario INVCustodia"""

    nombre_completo = StringField("Nombre completo", validators=[DataRequired(), Length(max=250)])
    fecha = DateField("Fecha", validators=[DataRequired()])
    curp = StringField("CURP", validators=[DataRequired(), Length(max=50)])
    guardar = SubmitField("Guardar")
