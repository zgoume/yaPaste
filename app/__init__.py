from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .models import Bin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def clean_expired_bins():
    with db.session.begin(subtransactions=True):  # Contexte sécurisé
        expired_bins = Bin.query.filter(Bin.expires_at <= datetime.utcnow()).all()
        for bin in expired_bins:
            db.session.delete(bin)
        db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    with app.app_context():
        from . import routes, admin_routes, Admin
        app.register_blueprint(routes.bp)
        app.register_blueprint(admin_routes.bp, url_prefix='/admin')

        db.create_all()

        # Vérifier s'il existe un administrateur
        if not Admin.query.first():
            print("Aucun administrateur configuré. Accédez à /setup-admin pour configurer le mot de passe.")

    # Tâches planifiées
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_expired_bins, 'interval', hours=1)  # Toutes les heures
    scheduler.start()

    return app
