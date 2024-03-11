"""
Requisiciones Catalogos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, FieldList, FormField, SelectField, StringField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime

from plataforma_web.blueprints.req_requisiciones.models import ReqRequisicion


class NoLabelMixin(object):
    def __init__(self, *args, **kwargs):
        super(NoLabelMixin, self).__init__(*args, **kwargs)
        for field_name in self._fields:
            field_property = getattr(self, field_name)
            field_property.label = None


class ReqCatalogoNewForm(FlaskForm):
    """Formulario articulo nuevo en Catalogo"""

    codigo = StringField("Código", validators=[Length(max=6), DataRequired()])
    descripcion = StringField("Descripción", validators=[Length(max=100), DataRequired()])
    unidad = SelectField("Unidad de medida", validators=[DataRequired()])
    categoria = SelectField("Categoría", validators=[DataRequired()])
    guardar = SubmitField("Guardar *")
