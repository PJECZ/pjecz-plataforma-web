"""
Requisiciones, formularios
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


class ArticulosForm(NoLabelMixin, FlaskForm):
    """Formulario de Articulos de la Requisicion"""

    codigo = IntegerField(render_kw={"readonly": True}, validators=[validators.optional()])
    descripcion = StringField(render_kw={"readonly": True}, validators=[Length(max=100)])
    unidad = StringField(render_kw={"readonly": True}, validators=[Length(max=50)])
    cantidad = IntegerField(render_kw={"readonly": True}, default=0, validators=[validators.optional()])
    clave = StringField(render_kw={"readonly": True}, validators=[Length(max=20)])
    detalle = StringField(render_kw={"readonly": True}, validators=[Length(max=256)])


class ReqRequisicionNewForm(FlaskForm):
    """Formulario Requisicion Nueva"""

    fecha = DateField("Fecha *", format="%Y-%m-%d", default=datetime.now())
    gasto = StringField("Gasto *", validators=[DataRequired(), Length(max=7)])
    area = SelectField("Area *", validators=[DataRequired()])
    glosa = StringField("Glosa *", validators=[Length(max=100)])
    programa = StringField("Programa *", validators=[Length(max=100)])
    fuente = StringField("Fuente de financiamiento *", validators=[Length(max=100)])
    areaFinal = StringField("Area final a quien se entregará *", validators=[Length(max=100)])
    fechaRequerida = DateField("Fecha requerida *", format="%Y-%m-%d", default=datetime.now())
    observaciones = TextAreaField("Observaciones *", validators=[Length(max=1024)])
    codigoTmp = SelectField("Código *", validators=[Length(max=30)], render_kw={"onChange": "buscarRegistro()"})
    descripcionTmp = StringField("Descripción *", validators=[Length(max=100)])
    unidadTmp = StringField("U. medida *", validators=[Length(max=50)])
    cantidadTmp = IntegerField("Cantidad *", default=0, validators=[validators.optional()])
    claveTmp = SelectField("Clave *", validators=[Length(max=20)])
    detalleTmp = StringField("Detalle *", validators=[Length(max=256)])
    articulos = FieldList(FormField(ArticulosForm), min_entries=20)
    guardar = SubmitField("Guardar *")