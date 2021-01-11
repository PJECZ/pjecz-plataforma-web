"""
UniversalMixin define las columnas y métodos comunes de todos los modelos
"""
from sqlalchemy.sql import func
from plataforma_web.extensions import db


class UniversalMixin(object):
    """ Columnas y métodos comunes a todas las tablas """

    creado = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    modificado = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())
    estatus = db.Column(db.String(1), server_default='A', nullable=False)

    def delete(self):
        """ Eliminar registro """
        if self.estatus == 'A':
            self.estatus = 'B'
            return self.save()
        return None

    def recover(self):
        """ Recuperar registro """
        if self.estatus == 'B':
            self.estatus = 'A'
            return self.save()
        return None

    def save(self):
        """ Guardar registro """
        db.session.add(self)
        db.session.commit()
        return self
