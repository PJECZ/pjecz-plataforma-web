"""
Google Cloud App Engine toma main.py
"""
from plataforma_web import app

app = app.create_app()


if __name__ == '__main__':
    app.run()
