from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models.models import db, User, Analysis, SystemAnalytics
from functools import wraps
from collections import defaultdict

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    total_analyses = Analysis.query.count()
    fake_count = Analysis.query.filter_by(result='FAKE').count()
    real_count = Analysis.query.filter_by(result='REAL').count()

    analytics = SystemAnalytics.query.first()
    api_usage = analytics.api_usage if analytics else 0

    recent_users = User.query.order_by(User.id.desc()).limit(1).all()
    viral_fakes = Analysis.query.filter_by(result='FAKE').order_by(Analysis.virality.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                          users_count=users_count,
                          total_analyses=total_analyses,
                          fake_count=fake_count,
                          real_count=real_count,
                          api_usage=api_usage,
                          viral_fakes=viral_fakes)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Cannot delete an admin!", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/retrain', methods=['POST'])
@login_required
@admin_required
def trigger_retrain():
    flash("Model retraining triggered (Mockup)", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/heatmap')
@login_required
@admin_required
def heatmap():
    return render_template('user/heatmap.html')

@admin_bp.route('/admin/heatmap/data')
@login_required
def heatmap_data():
    analyses = Analysis.query.order_by(Analysis.timestamp.desc()).all()

    points = []
    for a in analyses:
        points.append({
            'lat':        a.latitude,
            'lng':        a.longitude,
            'country':    a.country or 'Unknown',
            'city':       a.city or 'Unknown',
            'verdict':    a.result,
            'confidence': round(a.confidence, 1),
            'virality':   round(a.virality, 1),
            'intensity':  round(a.virality / 100, 2)
        })

    country_counts = defaultdict(int)
    for p in points:
        country_counts[p['country']] += 1

    stats = sorted(
        [{'country': k, 'total': v} for k, v in country_counts.items()],
        key=lambda x: x['total'],
        reverse=True
    )

    return jsonify({'points': points, 'stats': stats})