"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CIDProcedimientoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    titulo_procedimiento = StringField("Título", validators=[DataRequired(), Length(max=256)])
    codigo = StringField("Código", validators=[DataRequired(), Length(max=16)])
    revision = IntegerField("Revisión", validators=[DataRequired()])
    fecha = DateField("Fecha de elaboración", validators=[DataRequired()])
    objetivo = StringField("Objetivo", validators=[DataRequired()])
    alcance = StringField("Alcance", validators=[DataRequired()])
    documentos = StringField("Documentos", validators=[DataRequired()])
    definiciones = StringField("Definiciones", validators=[DataRequired()])
    responsabilidades = StringField("Responsabilidades", validators=[DataRequired()])
    desarrollo = StringField("Desarrollo", validators=[DataRequired()])
    registros = StringField("Registros", validators=[DataRequired()])
    cambios = StringField("Cambios", validators=[DataRequired()])
    elaboro_nombre = StringField("Nombre", validators=[Length(max=256)])
    elaboro_puesto = StringField("Puesto", validators=[Length(max=256)])
    elaboro_email = StringField("Correo", validators=[Length(max=256)])
    reviso_nombre = StringField("Nombre", validators=[Length(max=256)])
    reviso_puesto = StringField("Puesto", validators=[Length(max=256)])
    reviso_email = StringField("Correo", validators=[Length(max=256)])
    aprobo_nombre = StringField("Nombre", validators=[Length(max=256)])
    aprobo_puesto = StringField("Puesto", validators=[Length(max=256)])
    aprobo_email = StringField("Correo", validators=[Length(max=256)])
    guardar = SubmitField("Guardar")
