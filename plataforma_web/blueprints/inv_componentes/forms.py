"""
Componentes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from wtforms.ext.sqlalchemy.fields import QuerySelectField


from plataforma_web.blueprints.inv_categorias.models import INVCategorias

# from plataforma_web.blueprints.inv_equipos.models import INVEquipos


def categorias_opciones():
    """Seleccionar la categoria para select"""
    return INVCategorias.query.filter_by(estatus="A").order_by(INVCategorias.nombre).all()


# def equipos_opciones():
#     """Seleccionar el equipo para select"""
#     return INVEquipos.query.filter_by(estatus="A").order_by(INVEquipos.nombre).all()


class INVComponenteForm(FlaskForm):
    """Formulario INVComponente"""

    nombre = QuerySelectField(label="Nombre Categoria", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    # nombre = QuerySelectField(label="Nombre Equipo", query_factory=equipos_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    cantidad = IntegerField("Cantidad", validators=[DataRequired()])
    version = StringField("Versión", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
