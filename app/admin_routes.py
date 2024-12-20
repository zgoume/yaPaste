from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash
from .models import Admin, Bin, db
from .utils import admin_required, check_password_hash
from datetime import datetime

bp = Blueprint('admin_routes', __name__)

@bp.route('/setup-admin', methods=['GET', 'POST'])
def setup_admin():
    # Vérifier si un administrateur existe déjà
    if Admin.query.first():
        flash("Un administrateur existe déjà. Veuillez vous connecter.", "info")
        return redirect(url_for('admin_routes.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or password != confirm_password:
            flash("Les mots de passe ne correspondent pas ou sont vides.", "danger")
            return render_template('setup_admin.html')

        # Créer l'administrateur
        hashed_password = generate_password_hash(password)
        new_admin = Admin(username="admin", password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        flash("Mot de passe administrateur configuré avec succès. Veuillez vous connecter.", "success")
        return redirect(url_for('admin_routes.login'))

    return render_template('setup_admin.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            session['admin'] = admin.id
            return redirect(url_for('admin_routes.dashboard'))
        else:
            flash("Invalid credentials", "danger")

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('routes.home'))

@bp.route('/dashboard')
@admin_required
def dashboard():
    bins = Bin.query.all()
    # Calcul des statistiques
    total_bins = Bin.query.count()
    public_bins = Bin.query.filter_by(is_public=True).count()
    private_bins = total_bins - public_bins
    expired_bins = Bin.query.filter(Bin.expires_at <= datetime.utcnow()).count()

    stats = {
        "total_bins": total_bins,
        "public_bins": public_bins,
        "private_bins": private_bins,
        "expired_bins": expired_bins
    }

    return render_template('admin_dashboard.html', bins=bins, stats=stats)

@bp.route('/delete/<string:bin_id>', methods=['POST'])
@admin_required
def delete_bin(bin_id):
    bin = Bin.query.get_or_404(bin_id)
    db.session.delete(bin)
    db.session.commit()
    return redirect(url_for('admin_routes.dashboard'))

@bp.route('/stats')
@admin_required
def stats():
    total_bins = Bin.query.count()
    public_bins = Bin.query.filter_by(is_public=True).count()
    private_bins = total_bins - public_bins
    expired_bins = Bin.query.filter(Bin.expires_at <= datetime.utcnow()).count()

    return {
        "total_bins": total_bins,
        "public_bins": public_bins,
        "private_bins": private_bins,
        "expired_bins": expired_bins
    }

@bp.route('/delete-multiple', methods=['POST'])
@admin_required
def delete_multiple_bins():
    """
    Supprime plusieurs bins en fonction des IDs envoyés depuis le tableau de bord admin.
    """
    bin_ids = request.form.getlist('bin_ids')  # Récupère les IDs sélectionnés

    if not bin_ids:
        flash("Aucun bin sélectionné pour suppression.", "warning")
        return redirect(url_for('admin_routes.dashboard'))

    # Supprime les bins correspondants
    Bin.query.filter(Bin.id.in_(bin_ids)).delete(synchronize_session='fetch')
    db.session.commit()

    flash(f"{len(bin_ids)} bin(s) supprimé(s) avec succès.", "success")
    return redirect(url_for('admin_routes.dashboard'))
