"""
Tesis Jurisprudencias Funcionarios, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class TesisJurisprudenciaFuncionario(db.Model, UniversalMixin):
    """ TesisJurisprudenciaFuncionario """

    # Nombre de la tabla
    __tablename__ = 'tesis_jurisprudencias_funcionarios'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        """ Representación """
        return '<TesisJurisprudenciaFuncionario>'
