# ==============================================================================
# Study Plan Routes
# ------------------------------------------------------------------------------
# This is the definitive version that correctly passes the notification count
# to the template, fixing any potential UndefinedError.
# ==============================================================================

from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.services import firebase_service, leetcode_api
from collections import defaultdict

bp = Blueprint('study_plan', __name__)

@bp.route('/study-plan/')
def view_study_plan():
    username = session.get('leetcode_username')
    if not username:
        return redirect(url_for('auth.login'))

    plan_questions = firebase_service.get_study_plan_questions()
    user_progress = firebase_service.get_or_initialize_user_study_plan(username)
    
    # FIX: Fetch the count of pending friend requests for the navbar dot
    pending_requests_count = len(firebase_service.get_pending_requests(username))
    
    if not plan_questions:
        flash("The study plan questions have not been seeded yet. Run the seeder.", "error")
        # Pass the count even on redirect to prevent brief errors
        return redirect(url_for('dashboard.user_dashboard'))

    recent_submissions = leetcode_api.get_recent_submissions(username, 100)
    solved_slugs = {sub['titleSlug'] for sub in recent_submissions if sub['statusDisplay'] == 'Accepted'}

    grouped_questions = defaultdict(list)
    for question in plan_questions:
        grouped_questions[question.get('topic', 'General')].append(question)
    
    current_index = user_progress.get('current_question_index', 0)
    total_questions = len(plan_questions)
    
    # Check if the user has completed the entire plan
    if current_index >= total_questions:
        return render_template('study_plan.html', 
                               all_questions_completed=True,
                               grouped_questions=grouped_questions,
                               solved_slugs=solved_slugs,
                               pending_requests_count=pending_requests_count) # Pass the count

    current_question = plan_questions[current_index]
    is_current_solved = current_question['titleSlug'] in solved_slugs
            
    return render_template('study_plan.html', 
                           current_question=current_question, 
                           progress=user_progress, 
                           total_questions=total_questions,
                           is_current_solved=is_current_solved,
                           grouped_questions=grouped_questions,
                           solved_slugs=solved_slugs,
                           pending_requests_count=pending_requests_count) # Pass the count

@bp.route('/study-plan/next', methods=['POST'])
def advance_to_next_question():
    username = session.get('leetcode_username')
    if not username:
        return redirect(url_for('auth.login'))
        
    user_progress = firebase_service.get_or_initialize_user_study_plan(username)
    current_index = user_progress.get('current_question_index', 0)
    
    # This call advances the user's progress in the database
    firebase_service.advance_user_study_plan(username, current_index)
    
    return redirect(url_for('study_plan.view_study_plan'))