from plataforma_web.app import create_app
from plataforma_web.extensions import db


app = create_app()
db.app = app
