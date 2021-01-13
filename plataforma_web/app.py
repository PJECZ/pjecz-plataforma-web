"""
Flask App
"""
from flask import Flask
from plataforma_web.extensions import csrf, db, login_manager

from plataforma_web.blueprints.roles.views import roles
from plataforma_web.blueprints.usuarios.views import usuarios
from plataforma_web.blueprints.entradas_salidas.views import entradas_salidas
from plataforma_web.blueprints.bitacoras.views import bitacoras
from plataforma_web.blueprints.sistemas.views import sistemas
from plataforma_web.blueprints.abogados.views import abogados

from plataforma_web.blueprints.usuarios.models import Usuario


def create_app():
    """ Crear app """
    # Definir app
    app = Flask(__name__, instance_relative_config=True)
    # Cargar la configuración para producción en config/settings.py
    app.config.from_object('config.settings')
    # Cargar la configuración para desarrollo en instance/settings.py
    app.config.from_pyfile('settings.py', silent=True)
    # Cargar los blueprints
    app.register_blueprint(roles)
    app.register_blueprint(usuarios)
    app.register_blueprint(entradas_salidas)
    app.register_blueprint(bitacoras)
    app.register_blueprint(sistemas)
    app.register_blueprint(abogados)
    # Cargar las extensiones
    extensions(app)
    authentication(Usuario)
    # Entregar app
    return app

def extensions(app):
    """ Incorporar las extensiones """
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

def authentication(user_model):
    """ Inicializar Flask-Login """
    login_manager.login_view = 'usuarios.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)
