# ==============================================================================
# Social Routes (Friends, Requests, Leaderboard)
# ------------------------------------------------------------------------------
# This is the definitive version that correctly passes the notification count
# to all relevant templates, fixing the UndefinedError.
# ==============================================================================

import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import firebase_service, leetcode_api

bp = Blueprint('social', __name__)


@bp.route('/friends', methods=['GET', 'POST'])
def friends_page():
    """
    Handles displaying the user's current friends list (GET) and
    sending a new friend request (POST).
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        friend_username = request.form.get('friend_username', '').lower()
        user_data = firebase_service.get_user_data(main_username)
        current_friends = user_data.get('friends', [])
        
        if friend_username and friend_username != main_username and friend_username not in current_friends:
            if leetcode_api.get_user_stats(friend_username):
                result = firebase_service.create_friend_request(main_username, friend_username)
                flash(result, "info")
            else:
                flash(f"LeetCode user '{friend_username}' not found.", "error")
        elif friend_username in current_friends:
            flash(f"You are already friends with {friend_username}.", "info")
        elif friend_username == main_username:
            flash("You cannot send a friend request to yourself.", "error")
        
        return redirect(url_for('social.friends_page'))
    
    friend_usernames = firebase_service.get_friends(main_username)
    friends_data = [stats for username in friend_usernames if (stats := leetcode_api.get_user_stats(username))]
    
    # FIX: Fetch and pass the count for the navbar notification dot
    pending_requests_count = len(firebase_service.get_pending_requests(main_username))
    
    return render_template('friends.html', friends=friends_data, pending_requests_count=pending_requests_count)


@bp.route('/friends/remove/<string:friend_username>', methods=['POST'])
def remove_friend(friend_username):
    """
    Handles removing a friend from both the user's and the friend's lists.
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))
    
    friend_username_lower = friend_username.lower()
    firebase_service.remove_friend(main_username, friend_username_lower)
    firebase_service.remove_friend(friend_username_lower, main_username)
    
    flash(f"Removed {friend_username} from your friends.", "success")
    return redirect(url_for('social.friends_page'))


@bp.route('/leaderboard')
def leaderboard_page():
    """
    Handles displaying the leaderboard, which includes the user and their friends.
    """
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))

    my_stats = leetcode_api.get_user_stats(main_username)
    friend_list = firebase_service.get_friends(main_username)
    
    leaderboard_data = []
    if my_stats:
        leaderboard_data.append(my_stats)
    
    for friend_username in friend_list:
        stats = leetcode_api.get_user_stats(friend_username)
        if stats:
            leaderboard_data.append(stats)
            
    sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x.get('totalSolved', 0), reverse=True)
    
    # FIX: Fetch and pass the count for the navbar notification dot
    pending_requests_count = len(firebase_service.get_pending_requests(main_username))
    
    return render_template('leaderboard.html', 
                           leaderboard_data=sorted_leaderboard,
                           chart_data=sorted_leaderboard,
                           pending_requests_count=pending_requests_count)


@bp.route('/requests')
def requests_page():
    """Displays all pending friend requests for the current user."""
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))
        
    pending_requests = firebase_service.get_pending_requests(main_username)
    
    # The count is just the length of the list we already fetched
    return render_template('requests.html', requests=pending_requests, pending_requests_count=len(pending_requests))


@bp.route('/requests/respond/<string:request_id>/<string:action>', methods=['POST'])
def respond_to_request(request_id, action):
    """Handles the 'accept' or 'reject' action for a friend request."""
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))
        
    if action == 'accept':
        success = firebase_service.accept_friend_request(request_id)
        if success:
            flash("Friend request accepted!", "success")
        else:
            flash("Error accepting request. It may have been withdrawn.", "error")
    elif action == 'reject':
        firebase_service.reject_friend_request(request_id)
        flash("Friend request rejected.", "info")
    
    return redirect(url_for('social.requests_page'))