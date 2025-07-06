from flask import Blueprint, render_template, redirect, url_for, session, flash

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    if 'leetcode_username' in session:
        return redirect(url_for('dashboard.user_dashboard'))
    else:
        return redirect(url_for('auth.login'))

@bp.route('/logout')
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('auth.login'))

@bp.route('/settings')
def settings_page():
    if not session.get('leetcode_username'):
        return redirect(url_for('auth.login'))
    return render_template('settings.html')