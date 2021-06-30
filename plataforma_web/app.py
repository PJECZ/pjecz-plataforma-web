"""
Flask App
"""
from flask import Flask
from redis import Redis
import rq
from plataforma_web.extensions import csrf, db, login_manager, moment

from plataforma_web.blueprints.roles.views import roles
from plataforma_web.blueprints.usuarios.views import usuarios
from plataforma_web.blueprints.entradas_salidas.views import entradas_salidas
from plataforma_web.blueprints.bitacoras.views import bitacoras
from plataforma_web.blueprints.sistemas.views import sistemas
from plataforma_web.blueprints.tareas.views import tareas

from plataforma_web.blueprints.abogados.views import abogados
from plataforma_web.blueprints.audiencias.views import audiencias
from plataforma_web.blueprints.autoridades.views import autoridades
from plataforma_web.blueprints.distritos.views import distritos
from plataforma_web.blueprints.edictos.views import edictos
from plataforma_web.blueprints.glosas.views import glosas
from plataforma_web.blueprints.listas_de_acuerdos.views import listas_de_acuerdos
from plataforma_web.blueprints.materias.views import materias
from plataforma_web.blueprints.modulos.views import modulos
from plataforma_web.blueprints.peritos.views import peritos
from plataforma_web.blueprints.reportes.views import reportes
from plataforma_web.blueprints.resultados.views import resultados
from plataforma_web.blueprints.sentencias.views import sentencias
from plataforma_web.blueprints.transcripciones.views import transcripciones
from plataforma_web.blueprints.ubicaciones_expedientes.views import ubicaciones_expedientes

from plataforma_web.blueprints.cid_procedimientos.views import cid_procedimientos
from plataforma_web.blueprints.cid_formatos.views import cid_formatos
from plataforma_web.blueprints.cid_registros.views import cid_registros

from plataforma_web.blueprints.usuarios.models import Usuario


def create_app():
    """Crear app"""
    # Definir app
    app = Flask(__name__, instance_relative_config=True)
    # Cargar la configuración para producción en config/settings.py
    app.config.from_object("config.settings")
    # Cargar la configuración para desarrollo en instance/settings.py
    app.config.from_pyfile("settings.py", silent=True)
    # Redis
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue(app.config["TASK_QUEUE"], connection=app.redis, default_timeout=1920)
    # Cargar los blueprints
    app.register_blueprint(roles)
    app.register_blueprint(usuarios)
    app.register_blueprint(entradas_salidas)
    app.register_blueprint(bitacoras)
    app.register_blueprint(sistemas)
    app.register_blueprint(tareas)
    app.register_blueprint(abogados)
    app.register_blueprint(audiencias)
    app.register_blueprint(autoridades)
    app.register_blueprint(distritos)
    app.register_blueprint(edictos)
    app.register_blueprint(glosas)
    app.register_blueprint(listas_de_acuerdos)
    app.register_blueprint(materias)
    app.register_blueprint(modulos)
    app.register_blueprint(peritos)
    app.register_blueprint(reportes)
    app.register_blueprint(resultados)
    app.register_blueprint(sentencias)
    app.register_blueprint(transcripciones)
    app.register_blueprint(ubicaciones_expedientes)
    app.register_blueprint(cid_procedimientos)
    app.register_blueprint(cid_formatos)
    app.register_blueprint(cid_registros)
    # Cargar las extensiones
    extensions(app)
    authentication(Usuario)
    # Entregar app
    return app


def extensions(app):
    """Incorporar las extensiones"""
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)


def authentication(user_model):
    """Inicializar Flask-Login"""
    login_manager.login_view = "usuarios.login"

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)
