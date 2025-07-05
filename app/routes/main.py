from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services import leetcode_api, firebase_service

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('leetcode_username')
        if username:
            # Check if user exists on LeetCode (using our mock API)
            user_data = leetcode_api.get_user_stats(username)
            if user_data:
                # Add user to our Firebase DB
                firebase_service.add_or_update_user(username)
                # Store username in session
                session['leetcode_username'] = username
                return redirect(url_for('dashboard.user_dashboard'))
            else:
                # TODO: Add flash message for "user not found"
                return render_template('index.html', error="LeetCode user not found.")
    return render_template('index.html')

@bp.route('/logout')
def logout():
    session.pop('leetcode_username', None)
    return redirect(url_for('main.home'))
# ... (keep existing imports and home/logout routes) ...
@bp.route('/settings')
def settings_page():
    if not session.get('leetcode_username'):
        return redirect(url_for('main.home'))
    
    # This is a placeholder for now.
    return render_template('settings.html')