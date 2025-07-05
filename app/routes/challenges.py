from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('challenges', __name__)

@bp.route('/challenges')
def challenges_page():
    if not session.get('leetcode_username'):
        return redirect(url_for('main.home'))
    
    # This is a placeholder for now.
    # In the future, you would fetch challenges from Firebase here.
    return render_template('challenges.html')