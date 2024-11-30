from flask import Blueprint, request, render_template, redirect, url_for, abort, flash
from app.models import Bin, db
from app.utils import is_expired, hash_password, verify_password
from datetime import datetime, timedelta

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    """
    Page d'accueil pour créer un bin.
    """
    from .models import Admin
    if not Admin.query.first():
        return redirect(url_for('admin_routes.setup_admin'))
    
    return render_template('create_bin.html')


@bp.route('/create', methods=['POST'])
def create_bin():
    """
    Route pour créer un nouveau bin.
    """
    content = request.form.get('content')
    password = request.form.get('password')
    is_public = request.form.get('is_public') == 'on'
    single_read = request.form.get('single_read') == 'on'
    expires_in = request.form.get('expires_in', 0)

    # Calcul de la date d'expiration
    if expires_in:
        expires_at = datetime.utcnow() + timedelta(days=int(expires_in))
    else:
        expires_at = None

    # Hachage du mot de passe s'il existe
    hashed_password = hash_password(password) if password else None

    # Création d'un nouveau bin
    new_bin = Bin(
        content=content,
        password=hashed_password,
        is_public=is_public,
        single_read=single_read,
        expires_at=expires_at
    )
    db.session.add(new_bin)
    db.session.commit()

    flash("Bin créé avec succès.", "success")
    return redirect(url_for('routes.view_bin', bin_id=new_bin.id))


@bp.route('/bin/<string:bin_id>', methods=['GET', 'POST'])
def view_bin(bin_id):
    """
    Route pour afficher un bin.
    Si un mot de passe est requis, demande une validation.
    Si le bin est configuré pour une seule lecture, il est supprimé après consultation.
    """
    bin = Bin.query.get_or_404(bin_id)

    # Vérification de l'expiration
    if is_expired(bin.expires_at):
        db.session.delete(bin)
        db.session.commit()
        abort(404, "Ce bin a expiré.")

    if request.method == 'POST':
        # Vérification du mot de passe
        password = request.form.get('password')
        if bin.password and not verify_password(bin.password, password):
            flash("Mot de passe incorrect.", "danger")
            return render_template('view_bin.html', bin=bin, requires_password=True)

    # Suppression du bin après lecture unique
    if bin.single_read:
        db.session.delete(bin)
        db.session.commit()

    return render_template('view_bin.html', bin=bin, requires_password=False)
