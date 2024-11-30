import os

class Config:
    # Clé secrète pour les sessions Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')

    # Configuration de la base de données
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'bins.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
