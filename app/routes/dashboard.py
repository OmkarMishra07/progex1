# app/routes/dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for
from app.services import leetcode_api

bp = Blueprint('dashboard', __name__)

# THE FIX: Added a trailing slash to the route.
@bp.route('/dashboard/')
def user_dashboard():
    username = session.get('leetcode_username')
    if not username:
        return redirect(url_for('main.home'))

    stats = leetcode_api.get_user_stats(username)
    recent_problems = leetcode_api.get_recent_submissions(username, 20)
    daily = leetcode_api.get_daily_challenge()
    
    is_completed = False
    if daily:
        daily_slug = daily['link'].split('/problems/')[-1].strip('/')
        for sub in recent_problems:
            if sub['titleSlug'] == daily_slug and sub['statusDisplay'] == 'Accepted':
                is_completed = True
                break
    
    return render_template('dashboard.html', 
                           stats=stats, 
                           problems=recent_problems[:10],
                           daily=daily,
                           is_completed=is_completed)


# THE FIX: Also added a trailing slash here for consistency.
@bp.route('/daily/')
def daily_challenge_page():
    username = session.get('leetcode_username')
    if not username:
        return redirect(url_for('main.home'))
        
    daily = leetcode_api.get_daily_challenge()
    if not daily:
        return render_template('daily.html', daily=None, is_completed=False)
        
    recent_submissions = leetcode_api.get_recent_submissions(username, 20)
    is_completed = False
    daily_slug = daily['link'].split('/problems/')[-1].strip('/')
    
    for sub in recent_submissions:
        if sub['titleSlug'] == daily_slug and sub['statusDisplay'] == 'Accepted':
            is_completed = True
            break
            
    return render_template('daily.html', daily=daily, is_completed=is_completed)