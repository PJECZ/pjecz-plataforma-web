"""
Google Cloud App Engine toma main.py
"""
from plataforma_web import app

app = app.create_app()

# Esto solo opera cuando se ejecuta localmente
if __name__ == '__main__':
    app.run()
