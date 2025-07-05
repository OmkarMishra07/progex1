# ==============================================================================
# Friends & Leaderboard Routes
# ------------------------------------------------------------------------------
# This file defines the routes for all social features:
#   - /friends:      Display the friends list and handle adding new friends.
#   - /friends/remove: Handle the removal of a friend.
#   - /leaderboard:  Display a ranked list and chart comparing the user
#                    and their friends.
# ==============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import firebase_service, leetcode_api

# Create a Blueprint for these routes
bp = Blueprint('friends', __name__)


@bp.route('/friends', methods=['GET', 'POST'])
def friends_page():
    """
    Handles both displaying the friends list (GET) and adding a new
    friend via the form (POST).
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))

    # --- Handle Adding a New Friend (POST Request) ---
    if request.method == 'POST':
        friend_username = request.form.get('friend_username')
        
        # Basic validation
        if friend_username and friend_username != main_username:
            # Good practice: Check if the user exists on LeetCode before adding
            if leetcode_api.get_user_stats(friend_username):
                firebase_service.add_friend(main_username, friend_username)
                flash(f"Successfully added {friend_username} as a friend!", "success")
            else:
                flash(f"LeetCode user '{friend_username}' not found.", "error")
        elif friend_username == main_username:
            flash("You cannot add yourself as a friend.", "error")
        
        # Redirect back to the friends page after processing the form
        return redirect(url_for('friends.friends_page'))
    
    # --- Fetch and Display Friends (GET Request) ---
    # 1. Get the list of friend usernames from our Firebase database
    friend_usernames = firebase_service.get_friends(main_username)
    
    # 2. Fetch the full LeetCode profile stats for each friend
    friends_data = []
    for username in friend_usernames:
        stats = leetcode_api.get_user_stats(username)
        if stats:
            # Only add the friend to the display list if we successfully got their stats
            friends_data.append(stats)
            
    # 3. Pass the list of detailed friend data to the HTML template
    return render_template('friends.html', friends=friends_data)


@bp.route('/friends/remove/<string:friend_username>', methods=['POST'])
def remove_friend(friend_username):
    """
    Handles the removal of a friend. This is a POST-only route to prevent
    accidental removal via a simple link click.
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))
    
    firebase_service.remove_friend(main_username, friend_username)
    flash(f"Removed {friend_username} from your friends.", "success")
    return redirect(url_for('friends.friends_page'))


@bp.route('/leaderboard')
def leaderboard_page():
    """
    Fetches data for the user and all their friends, sorts it, and
    passes it to the leaderboard template for both the table and the chart.
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))

    # 1. Get the current user's own stats to include them in the leaderboard
    my_stats = leetcode_api.get_user_stats(main_username)
    
    # 2. Get the list of friend usernames from Firebase
    friend_list = firebase_service.get_friends(main_username)
    
    leaderboard_data = []
    if my_stats:
        leaderboard_data.append(my_stats)
    
    # 3. Fetch the stats for every friend and add them to the list
    for friend_username in friend_list:
        stats = leetcode_api.get_user_stats(friend_username)
        if stats:
            leaderboard_data.append(stats)
            
    # 4. Sort the combined list by total problems solved (in descending order)
    sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['totalSolved'], reverse=True)
    
    # 5. Pass the raw Python list to the template. The Jinja `tojson` filter
    #    will handle converting it correctly for the JavaScript chart.
    return render_template('leaderboard.html', 
                           leaderboard_data=sorted_leaderboard,
                           chart_data=sorted_leaderboard)