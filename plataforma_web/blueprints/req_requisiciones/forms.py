"""
Requisiciones, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, FieldList, FormField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, validators
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
    justificacion = TextAreaField("Justificacion", validators=[Length(max=1024)])
    codigoTmp = SelectField("Código *", validators=[Length(max=30)], render_kw={"onChange": "buscarRegistro()"})
    descripcionTmp = StringField("Descripción *", validators=[Length(max=100)])
    unidadTmp = StringField("U. medida *", validators=[Length(max=50)])
    cantidadTmp = IntegerField("Cantidad *", default=0, validators=[validators.optional()])
    claveTmp = SelectField("Clave *", validators=[Length(max=20)])
    detalleTmp = StringField("Detalle *", validators=[Length(max=256)])
    articulos = FieldList(FormField(ArticulosForm), min_entries=20)
    guardar = SubmitField("Guardar *")


class ReqRequisicionStep2RequestForm(FlaskForm):
    """Formulario Requisicion (step 2 request) Solicitar"""

    solicito_nombre = StringField("Usted es")  # Read only
    solicito_puesto = StringField("Su puesto")  # Read only
    solicito_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    solicitar = SubmitField("Solicitar")


class ReqRequisicionCancel2RequestForm(FlaskForm):
    """Formulario Requisicion (step 2 request) Solicitar"""

    solicito_nombre = StringField("Usted es")  # Read only
    solicito_puesto = StringField("Su puesto")  # Read only
    solicito_email = StringField("Su e-mail")  # Read only
    motivo = StringField("Motivo", validators=[DataRequired(), Length(max=256)])
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    cancelar = SubmitField("Cancelar")


class ReqRequisicionStep3AuthorizeForm(FlaskForm):
    """Formulario Requisicion (step 3 authorize) Autorizar"""

    autorizo_nombre = StringField("Usted es")  # Read only
    autorizo_puesto = StringField("Su puesto")  # Read only
    autorizo_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    autorizar = SubmitField("Autorizar")


class ReqRequisicionStep4ReviewForm(FlaskForm):
    """Formulario Requisicion (step 4 review) Revisar"""

    reviso_nombre = StringField("Usted es")  # Read only
    reviso_puesto = StringField("Su puesto")  # Read only
    reviso_email = StringField("Su e-mail")  # Read only
    contrasena = PasswordField("Contraseña de su firma electrónica", validators=[DataRequired(), Length(6, 64)])
    revisar = SubmitField("Revisar")
