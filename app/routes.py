from flask import Blueprint, request, render_template, redirect, url_for, abort, flash, session
from app.models import Bin, db
from app.utils import is_expired, hash_password, verify_password
from datetime import datetime, timedelta
import sys

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    """
    Page d'accueil pour créer un bin.
    """
    from .models import Admin
    if not Admin.query.first():
        return redirect(url_for('admin_routes.setup_admin'))
    
    public_bins = Bin.query.filter_by(is_public=True).order_by(Bin.created_at.desc()).limit(10).all()  # Récupère les 10 bins publics les plus récents
    return render_template('create_bin.html', public_bins=public_bins)


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

    # Récupération de l'adresse IP à partir de l'en-tête X-Forwarded-For
    if 'X-Forwarded-For' in request.headers:
        creator_ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    else:
        creator_ip = request.remote_addr  # Fallback si X-Forwarded-For n'est pas présent

    # Création d'un nouveau bin
    new_bin = Bin(
        content=content,
        password=hashed_password,
        is_public=is_public,
        single_read=single_read,
        expires_at=expires_at,
        creator_ip=creator_ip
    )
    db.session.add(new_bin)
    db.session.commit()

    # Stocke l'ID du bin dans la session pour marquer qu'il a été récemment créé
    session['recently_created_bin'] = new_bin.id

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

    print('DEBUG View BIN', file=sys.stderr)

    # Vérifie si le bin a été récemment créé
    recently_created = session.pop('recently_created_bin', None) == bin_id
    if recently_created:
        print('DEBUG Recently Created == True', file=sys.stderr)
        return render_template('view_bin.html', bin=bin, requires_password=False)

    if request.method == 'POST':
        # Vérification du mot de passe
        password = request.form.get('password')
        if bin.password and verify_password(bin.password, password):
            return render_template('view_bin.html', bin=bin, requires_password=False)
        else:
            flash("Mot de passe incorrect.", "danger")
            return render_template('view_bin.html', bin=bin, requires_password=True)


    # Suppression du bin après lecture unique
    if bin.single_read:
        db.session.delete(bin)
        db.session.commit()

    return render_template('view_bin.html', bin=bin, requires_password=bin.password is not None)
