# ==============================================================================
# Dashboard Routes
# ------------------------------------------------------------------------------
# This is the definitive version that correctly passes the notification count
# to the template, fixing the UndefinedError.
# ==============================================================================

from flask import Blueprint, render_template, session, redirect, url_for, flash
# We need to import firebase_service to get the request count
from app.services import leetcode_api, firebase_service 

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/')
def user_dashboard():
    """
    Renders the main dashboard page for the logged-in user.
    Fetches user stats, recent submissions, and friend request count.
    """
    username = session.get('leetcode_username')
    if not username:
        return redirect(url_for('main.home'))

    # Fetch the primary user stats from the API service.
    stats = leetcode_api.get_user_stats(username)
    
    # FIX: Initialize the count here to ensure it always has a value
    pending_requests_count = 0
    
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
        # If stats were fetched successfully, get the other necessary data.
        problems = leetcode_api.get_recent_submissions(username, 10)
        # FIX: Fetch the count of pending friend requests
        pending_requests_count = len(firebase_service.get_pending_requests(username))

    # Render the template, passing all necessary data, including the new count.
    return render_template('dashboard.html', 
                           stats=stats, 
                           problems=problems,
                           pending_requests_count=pending_requests_count)

# The '/daily' route has been removed.