# ==============================================================================
# Dashboard Routes
# ------------------------------------------------------------------------------
# This file handles the logic for the main user dashboard.
# The /daily route and all related logic have been removed for simplification.
# ==============================================================================

from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.services import leetcode_api

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/')
def user_dashboard():
    """
    Renders the main dashboard page for the logged-in user.
    Fetches user stats and recent submissions.
    """
    username = session.get('leetcode_username')
    if not username:
        return redirect(url_for('main.home'))

    # Fetch the primary user stats from the API service.
    stats = leetcode_api.get_user_stats(username)
    
    # This is a crucial error check. If the API fails, we prevent a crash.
    if not stats:
        flash("Error: Could not fetch your LeetCode data at this time. The API might be down or the username is invalid. Please try again later.", "error")
        # Provide a fallback stats object to prevent the template from crashing.
        stats = {
            'username': username, 'avatar': '', 'totalSolved': '?', 'globalRanking': '?', 
            'streak': '?', 'maxStreak': '?', 'easySolved': '?', 'mediumSolved': '?', 'hardSolved': '?'
        }
        problems = []
    else:
        # If stats were fetched successfully, get the recent submissions.
        problems = leetcode_api.get_recent_submissions(username, 10)

    # Render the template, passing only the necessary data.
    return render_template('dashboard.html', 
                           stats=stats, 
                           problems=problems)

# The '/daily' route and its function 'daily_challenge_page()' have been completely removed.