"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, HiddenField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento


class CIDProcedimientoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Título", validators=[DataRequired(), Length(max=256)])
    codigo = StringField("Código", validators=[DataRequired(), Length(max=16)])
    revision = IntegerField("Revisión", validators=[DataRequired()])
    fecha = DateField("Fecha de elaboración", validators=[DataRequired()])
    etapa = SelectField("Etapa", choices=CIDProcedimiento.ETAPAS, validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class CIDProcedimientoObjetivoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    objetivo = HiddenField("Objetivo", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")


class CIDProcedimientoAlcanceForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    alcance = HiddenField("Alcance", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")


class CIDProcedimientoDocumentosForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    documentos = HiddenField("Documentos", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")


class CIDProcedimientoDefinicionesForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    definiciones = HiddenField("Definiciones", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")


class CIDProcedimientoResponsabilidadesForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    responsabilidades = HiddenField("Responsabilidades", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")


class CIDProcedimientoDesarrolloForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    desarrollo = HiddenField("Desarrollo", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")


class CIDProcedimientoGestionRiesgosForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Distrito")  # Read only
    gestion_riesgos = HiddenField("GestionRiesgos", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")
