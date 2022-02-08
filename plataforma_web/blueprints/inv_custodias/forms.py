"""
Componentes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional

from wtforms.ext.sqlalchemy.fields import QuerySelectField


# from plataforma_web.blueprints.usuarios.models import Usuarios

# from plataforma_web.blueprints.oficinas.models import oficinas


# def usuarios_opciones():
#     """Seleccionar el usuario para select"""
#     return Usuarios.query.filter_by(estatus="A").order_by(Usuarios.nombre).all()


# def equipos_opciones():
#     """Seleccionar la oficina para select"""
#     return oficinas.query.filter_by(estatus="A").order_by(oficinas.nombre).all()


class INVCustodiasForm(FlaskForm):
    """Formulario INVCustodias"""

    # nombre = QuerySelectField(label="Nombre Categoria", query_factory=categorias_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    # nombre = QuerySelectField(label="Nombre Equipo", query_factory=equipos_opciones, get_label="nombre", validators=[DataRequired()])  # solo lectrua
    fecha = DateField("Descripción", validators=[DataRequired()])
    curp = StringField("CURP", validators=[DataRequired(), Length(max=50)])
    nombre_completo = StringField("Nombre completo", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
