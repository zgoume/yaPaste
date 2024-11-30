from datetime import datetime
from app import db
import secrets
import string
from .utils import generate_random_id

class Bin(db.Model):
    id = db.Column(db.String(8), primary_key=True, default=lambda: generate_random_id())
    content = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(128), nullable=True)  # Haché
    is_public = db.Column(db.Boolean, default=True)
    single_read = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)