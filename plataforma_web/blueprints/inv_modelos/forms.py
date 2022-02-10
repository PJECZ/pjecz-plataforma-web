"""
Modelos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField


from plataforma_web.blueprints.inv_marcas.models import INVMarca


def marcas_opciones():
    """Seleccionar la marca para select"""
    return INVMarca.query.filter_by(estatus="A").order_by(INVMarca.nombre).all()


class INVModeloForm(FlaskForm):
    """Formulario INVModelo"""

    nombre = QuerySelectField(label="Nombre Marca", query_factory=marcas_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
