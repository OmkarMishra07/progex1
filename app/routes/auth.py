# ==============================================================================
# Friends & Leaderboard Routes
# ------------------------------------------------------------------------------
# This file defines the routes for all social features.
# All friend username inputs are converted to lowercase for consistency.
# ==============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import firebase_service, leetcode_api
import json

bp = Blueprint('friends', __name__)


@bp.route('/friends', methods=['GET', 'POST'])
def friends_page():
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # FIX: Convert friend's username to lowercase
        friend_username = request.form.get('friend_username', '').lower()
        
        if friend_username and friend_username != main_username:
            if leetcode_api.get_user_stats(friend_username):
                firebase_service.add_friend(main_username, friend_username)
                flash(f"Successfully added {friend_username} as a friend!", "success")
            else:
                flash(f"LeetCode user '{friend_username}' not found.", "error")
        elif friend_username == main_username:
            flash("You cannot add yourself as a friend.", "error")
        
        return redirect(url_for('friends.friends_page'))
    
    friend_usernames = firebase_service.get_friends(main_username)
    
    friends_data = []
    for username in friend_usernames:
        stats = leetcode_api.get_user_stats(username)
        if stats:
            friends_data.append(stats)
            
    return render_template('friends.html', friends=friends_data)


@bp.route('/friends/remove/<string:friend_username>', methods=['POST'])
def remove_friend(friend_username):
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))
    
    # FIX: Ensure username is lowercase for removal operation
    firebase_service.remove_friend(main_username, friend_username.lower())
    flash(f"Removed {friend_username} from your friends.", "success")
    return redirect(url_for('friends.friends_page'))


@bp.route('/leaderboard')
def leaderboard_page():
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
            
    sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['totalSolved'], reverse=True)
    
    return render_template('leaderboard.html', 
                           leaderboard_data=sorted_leaderboard,
                           chart_data=sorted_leaderboard)