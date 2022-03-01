"""
Componentes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from wtforms.ext.sqlalchemy.fields import QuerySelectField


from plataforma_web.blueprints.inv_categorias.models import INVCategoria

# from plataforma_web.blueprints.inv_equipos.models import INVEquipos


def categorias_opciones():
    """Seleccionar la categoria para select"""
    return INVCategoria.query.filter_by(estatus="A").order_by(INVCategoria.nombre).all()


class INVComponenteForm(FlaskForm):
    """Formulario INVComponente"""

    equipo = StringField("Numero inventario equipo")  # solo lectrua
    nombre = QuerySelectField(label="Categoria", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    cantidad = IntegerField("Cantidad", validators=[DataRequired()])
    version = StringField("Versión", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
