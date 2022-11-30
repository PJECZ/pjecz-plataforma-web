"""
not_escrituras, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Optional

from lib.wtforms import JSONField

from plataforma_web.blueprints.not_escrituras.models import NotEscritura

# from plataforma_web.blueprints.autoridades.models import Autoridad


# def autoridad_opciones():
#     """Autoridad: opciones para select"""
#     return Autoridad.query.filter_by(estatus="A").order_by(Autoridad.es_jurisdiccional).all()


class NotEscrituraForm(FlaskForm):
    """Formulario NotEscritura"""

    distrito = StringField("Distrito")  # Read only
    notaria = StringField("Notaría")  # Read only
    # juzgado = QuerySelectField("Juzgado", query_factory=autoridad_opciones, get_label="descripcion", validators=[DataRequired()])
    juzgado = SelectField("Juzgado", coerce=int, validate_choice=False, validators=[DataRequired()])
    estado = SelectField("Estado", choices=NotEscritura.ESTADOS, validators=[DataRequired()])
    contenido = JSONField("Contenido", validators=[Optional()])
    guardar = SubmitField("Guardar")
