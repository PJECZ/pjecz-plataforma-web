"""
Inventarios Modelos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField


from plataforma_web.blueprints.inv_marcas.models import InvMarca


def marcas_opciones():
    """Seleccionar la marca para select"""
    return InvMarca.query.filter_by(estatus="A").order_by(InvMarca.nombre).all()


class InvModeloForm(FlaskForm):
    """Formulario InvModelo"""

    nombre = QuerySelectField(label="Marca", query_factory=marcas_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    descripcion = StringField("Descripción del modelo", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")


class InvModeloEditForm(FlaskForm):
    """Formulario InvModelo"""

    nombre = StringField("Marca")  # solo lectrua
    descripcion = StringField("Descripción del modelo", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
