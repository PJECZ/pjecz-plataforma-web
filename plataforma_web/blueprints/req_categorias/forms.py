"""
Requisiciones Categorias, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.req_categorias.models import ReqCategoria


class NoLabelMixin(object):
    def __init__(self, *args, **kwargs):
        super(NoLabelMixin, self).__init__(*args, **kwargs)
        for field_name in self._fields:
            field_property = getattr(self, field_name)
            field_property.label = None


class ReqCategoriaNewForm(FlaskForm):
    """Formulario Categoria nueva"""

    descripcion = StringField("Descripción", validators=[Length(max=100), DataRequired()])
    guardar = SubmitField("Guardar *")
