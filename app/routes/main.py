# ==============================================================================
# Main Application Routes
# ------------------------------------------------------------------------------
# This file contains the core, non-feature-specific routes for the app.
# ==============================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.services import firebase_service

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    """
    Acts as the main entry point.
    - If a user is logged in, redirect them straight to their dashboard.
    - If they are NOT logged in, show the new landing page.
    """
    if 'leetcode_username' in session:
        return redirect(url_for('dashboard.user_dashboard'))
    else:
        return render_template('landing.html')


@bp.route('/logout')
def logout():
    """
    Logs the user out by clearing the session and redirects to the landing page.
    """
    session.clear()
    flash("You have been successfully logged out.", "info")
    # Redirect to the new landing page after logout
    return redirect(url_for('main.home'))


@bp.route('/settings')
def settings_page():
    """
    A placeholder route for the future settings page.
    """
    if not session.get('leetcode_username'):
        return redirect(url_for('auth.login'))
    
    return render_template('settings.html')
@bp.route('/seed-database')
def seed_database_route():
    """
    A special, hidden route for developers to automatically populate the
    database with sample data for testing.
    """
    result = firebase_service.seed_database()
    flash(result, 'info')
    return redirect(url_for('auth.login'))