# ==============================================================================
# Main Application Routes
# ------------------------------------------------------------------------------
# This file contains the core, non-feature-specific routes for the app,
# including the developer routes for seeding the database.
# ==============================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.services import firebase_service
from werkzeug.security import check_password_hash # Needed for delete_account
from flask import request # Needed for delete_account

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
    return redirect(url_for('main.home'))


@bp.route('/settings', methods=['GET'])
def settings_page():
    """
    Renders the main settings page.
    """
    if not session.get('leetcode_username'):
        return redirect(url_for('auth.login'))
    
    return render_template('settings.html')


@bp.route('/delete-account', methods=['POST'])
def delete_account():
    """
    Handles the account deletion request.
    Requires password confirmation for security.
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))

    password = request.form.get('password')
    user_data = firebase_service.get_user_data(main_username)
    
    if user_data and check_password_hash(user_data.get('password_hash', ''), password):
        success = firebase_service.delete_user_account(main_username)
        if success:
            session.clear()
            flash('Your account has been permanently deleted.', 'info')
            return redirect(url_for('main.home'))
        else:
            flash('An error occurred while deleting your account. Please try again.', 'error')
            return redirect(url_for('main.settings_page'))
    else:
        flash('Incorrect password. Account deletion cancelled.', 'error')
        return redirect(url_for('main.settings_page'))


# --- Developer Seeder Routes ---

@bp.route('/seed-database')
def seed_database_route():
    """
    A special, hidden route for developers to automatically populate the
    database with sample user data for testing.
    """
    result = firebase_service.seed_database()
    flash(result, 'info')
    return redirect(url_for('auth.login'))


@bp.route('/seed-neetcode-plan')
def seed_neetcode_route():
    """
    A special, hidden route for developers to automatically populate the
    database with the NeetCode 150 study plan questions.
    """
    result = firebase_service.seed_neetcode_plan()
    flash(result, 'info')
    # Redirect to the study plan page so you can immediately see the result
    return redirect(url_for('study_plan.view_study_plan'))
@bp.route('/about')
def about_page():
    pending_requests_count = 0
    if 'leetcode_username' in session:
        pending_requests_count = len(firebase_service.get_pending_requests(session['leetcode_username']))
    return render_template('about.html', pending_requests_count=pending_requests_count)
