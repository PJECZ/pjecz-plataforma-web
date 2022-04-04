"""
Inventarios Componentes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.inv_categorias.models import InvCategoria


def categorias_opciones():
    """Seleccionar la categoria para select"""
    return InvCategoria.query.filter_by(estatus="A").order_by(InvCategoria.nombre).all()


class InvComponenteForm(FlaskForm):
    """Formulario InvComponente"""

    inv_equipo = StringField("ID equipo")  # solo lectrua
    inv_marca = StringField("Marca")  # solo lectrua
    descripcion_equipo = StringField("Descripción del equipo")  # solo lectrua
    usuario = StringField("Usuario")  # solo lectrua
    nombre = QuerySelectField(label="Categoria", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    cantidad = IntegerField("Cantidad (Número entero apartir de 1)", validators=[DataRequired()])
    version = StringField("Versión", validators=[Optional(), Length(max=512)])
    guardar = SubmitField("Guardar")
