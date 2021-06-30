"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CIDProcedimientoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=128)])
    codigo = StringField("Código")
    contenido = HiddenField("Contenido", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")

"""
    descripcion = db.Column(db.String(256), nullable=False)
    codigo = db.Column(db.String(16), nullable=False)
    revision = db.Column(db.Integer(), nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    contenido = db.Column(db.Text(), nullable=False)
"""
