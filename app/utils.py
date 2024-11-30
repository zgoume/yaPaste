from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash

def is_expired(expires_at):
    """
    Vérifie si une date donnée est dans le passé (expirée).
    :param expires_at: datetime ou None
    :return: bool
    """
    if expires_at is None:
        return False
    return datetime.utcnow() > expires_at

def hash_password(password):
    """
    Hache un mot de passe en utilisant Werkzeug.
    :param password: str
    :return: str (mot de passe haché)
    """
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    """
    Vérifie si un mot de passe correspond à son haché.
    :param hashed_password: str
    :param password: str
    :return: bool
    """
    return check_password_hash(hashed_password, password)

def generate_unique_id():
    """
    Génère un identifiant unique pour un bin.
    :return: str
    """
    return str(uuid.uuid4())

def format_datetime(value):
    """
    Formate une date pour l'afficher de manière lisible.
    :param value: datetime
    :return: str (date formatée)
    """
    if value is None:
        return "No Expiration"
    return value.strftime('%Y-%m-%d %H:%M:%S')

def admin_required(f):
    """
    Middleware pour protéger les routes admin.
    Redirige vers la page de connexion si l'utilisateur n'est pas authentifié.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:  # Vérifie si la session admin existe
            flash("Vous devez être connecté en tant qu'administrateur pour accéder à cette page.", "danger")
            return redirect(url_for('admin_routes.login'))  # Redirige vers la page de connexion
        return f(*args, **kwargs)
    return decorated_function
