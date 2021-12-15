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

    # Clave foránea
    tesis_jurisprudencias_id = db.Column(db.Integer, db.ForeignKey('tesis_jurisprudencias.id'), index=True, nullable=False)
    tesis_jurisprudencias = db.relationship('TesisJurisprudencia', back_populates='tesis_jurisprudencias_funcionarios')
    

    # Clave foránea
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), index=True, nullable=False)
    funcionario = db.relationship('Funcionario', back_populates='tesis_jurisprudencias_funcionarios')
    

    def __repr__(self):
        """ Representación """
        return '<TesisJurisprudenciaFuncionario>'
