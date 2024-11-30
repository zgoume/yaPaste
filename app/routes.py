from flask import Blueprint, request, render_template, redirect, url_for, abort
from werkzeug.security import check_password_hash
from .models import Bin, db
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    return render_template('create_bin.html')

@bp.route('/create', methods=['POST'])
def create_bin():
    # Code pour créer un bin
    pass

@bp.route('/bin/<int:bin_id>', methods=['GET', 'POST'])
def view_bin(bin_id):
    # Code pour afficher un bin
    pass