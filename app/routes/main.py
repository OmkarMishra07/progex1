from flask import Blueprint, render_template, redirect, url_for, session

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    """
    Acts as the main entry point. Redirects users based on login status.
    """
    if 'leetcode_username' in session:
        return redirect(url_for('dashboard.user_dashboard'))
    else:
        return redirect(url_for('auth.login'))


@bp.route('/logout')
def logout():
    """
    Logs the user out by clearing the session.
    """
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/settings')
def settings_page():
    """
    A placeholder route for the future settings page.
    """
    if not session.get('leetcode_username'):
        return redirect(url_for('auth.login'))
    
    return render_template('settings.html')