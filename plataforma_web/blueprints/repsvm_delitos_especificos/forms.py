"""
REPSVM Delitos Especificos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.repsvm_delitos_genericos.models import REPSVMDelitoGenerico


def repsvm_delitos_genericos_opciones():
    """REPSVM Delitos Genericos: opciones para select"""
    return REPSVMDelitoGenerico.query.filter_by(estatus="A").order_by(REPSVMDelitoGenerico.nombre).all()


class REPSVMDelitoEspecificoForm(FlaskForm):
    """Formulario REPSVMDelitoEspecifico"""

    repsvm_delito_generico = QuerySelectField(query_factory=repsvm_delitos_genericos_opciones, get_label="nombre", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
