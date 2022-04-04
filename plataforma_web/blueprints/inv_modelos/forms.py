"""
Inventarios Modelos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


from plataforma_web.blueprints.inv_marcas.models import InvMarca


def marcas_opciones():
    """Seleccionar la marca para select"""
    return InvMarca.query.filter_by(estatus="A").order_by(InvMarca.nombre).all()


class InvModeloForm(FlaskForm):
    """Formulario InvModelo"""

    nombre = StringField("Marca", validators=[DataRequired()])  # solo lectrua
    descripcion = StringField("Descripción del modelo", validators=[DataRequired(), Length(max=512)])
    guardar = SubmitField("Guardar")
