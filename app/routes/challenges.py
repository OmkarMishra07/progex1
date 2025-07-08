# ==============================================================================
# Challenge Routes
# ------------------------------------------------------------------------------
# This file handles all logic for the challenges feature, including:
# - Displaying invitations, pending, ongoing, and completed challenges.
# - Automatically calculating progress for individuals and the entire group.
# - Creating new challenges and responding to invitations.
# - Editing and deleting challenges created by the user.
# ==============================================================================

import datetime
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.services import firebase_service, leetcode_api

bp = Blueprint('challenges', __name__)

# This helper function calculates the number of solved problems for a given user
def calculate_progress(user_submissions, challenge_problems):
    # Ensure lists are not None before creating the set
    if not user_submissions: user_submissions = []
    if not challenge_problems: return 0
    
    # Create a set of slugs for all accepted submissions for fast lookups
    solved_slugs = {sub['titleSlug'] for sub in user_submissions if sub['statusDisplay'] == 'Accepted'}
    solved_count = 0
    for problem in challenge_problems:
        # Check if the slug from the challenge exists in the user's solved set
        if problem.get('titleSlug') in solved_slugs:
            solved_count += 1
    return solved_count

@bp.route('/challenges/')
def challenges_page():
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('main.home'))
    
    # 1. Fetch all challenges this user is a part of
    all_challenges = firebase_service.get_user_challenges(main_username)
    
    # 2. Efficiently fetch submission data for all unique participants ONCE
    unique_participants = {main_username}
    for challenge in all_challenges:
        for participant in challenge.get('participants', {}).keys():
            unique_participants.add(participant)
            
    submissions_cache = {
        username: leetcode_api.get_recent_submissions(username, 50) 
        for username in unique_participants
    }
    
    # 3. Initialize lists to categorize challenges
    invitations, pending, ongoing, completed_expired = [], [], [], []
    
    # 4. Process each challenge to determine its status and progress
    for challenge in all_challenges:
        user_status = challenge.get('participants', {}).get(main_username, {}).get('status')
        if not user_status: continue # Failsafe for corrupted data

        challenge['user_status'] = user_status
        
        # Calculate time remaining
        expires_at = challenge.get('expiresAt')
        is_expired = False
        if expires_at and expires_at < datetime.datetime.now(expires_at.tzinfo):
            is_expired = True
            challenge['time_left'] = "Expired"
        elif expires_at:
            time_left = expires_at - datetime.datetime.now(expires_at.tzinfo)
            days, rem = divmod(time_left.total_seconds(), 86400)
            hours, _ = divmod(rem, 3600)
            challenge['time_left'] = f"{int(days)}d {int(hours)}h left"
        
        challenge_problems = challenge.get('problems', [])
        total_count = len(challenge_problems)
        user_submissions = submissions_cache.get(main_username, [])
        solved_count = calculate_progress(user_submissions, challenge_problems)
        
        challenge.update({
            'progress': solved_count,
            'total_problems': total_count,
            'progress_percent': (solved_count / total_count * 100) if total_count > 0 else 0,
            'is_completed_by_user': (solved_count >= total_count) if total_count > 0 else False
        })
        
        # Categorize all participants for detailed view
        participants_completed, participants_inprogress, participants_invited = [], [], []
        accepted_participants_names = []
        
        for name, data in challenge.get('participants', {}).items():
            status = data.get('status')
            p_info = {'username': name}
            if status == 'accepted':
                accepted_participants_names.append(name)
                p_progress = calculate_progress(submissions_cache.get(name, []), challenge_problems)
                if p_progress >= total_count:
                    participants_completed.append(p_info)
                else:
                    participants_inprogress.append(p_info)
            elif status == 'invited':
                participants_invited.append(p_info)
        
        challenge.update({
            'participants_completed': participants_completed,
            'participants_inprogress': participants_inprogress,
            'participants_invited': participants_invited
        })
        
        challenge_has_enough_players = len(accepted_participants_names) >= 2
        is_fully_completed = bool(accepted_participants_names) and not participants_inprogress and not participants_invited
        challenge['is_fully_completed'] = is_fully_completed

        # 5. Sort the challenge into the correct category based on its state
        if user_status == 'invited' and not is_expired:
            invitations.append(challenge)
        elif user_status == 'accepted' and not is_expired and not challenge_has_enough_players:
            pending.append(challenge)
        elif user_status == 'accepted' and not is_expired and not is_fully_completed:
            ongoing.append(challenge)
        else: # Covers declined, expired, and fully completed challenges
            completed_expired.append(challenge)
            
    return render_template('challenges.html', 
                           invitations=invitations,
                           pending=pending,
                           ongoing=ongoing, 
                           completed_expired=completed_expired)


@bp.route('/challenges/create', methods=['GET', 'POST'])
def create_challenge():
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        problems_text = request.form.get('problems')
        expires_str = request.form.get('expiresAt')
        invited_friends = request.form.getlist('friends')

        if not all([title, description, problems_text, expires_str]):
            flash("All fields are required.", "error")
            return redirect(url_for('challenges.create_challenge'))
        
        problem_slugs_raw = [slug.strip() for slug in problems_text.split(',') if slug.strip()]
        problems_list = []
        for slug_or_title in problem_slugs_raw:
            sanitized_slug = slug_or_title.lower().replace(' ', '-')
            display_title = sanitized_slug.replace('-', ' ').title()
            problems_list.append({'title': display_title, 'titleSlug': sanitized_slug})

        expires_at = datetime.datetime.strptime(expires_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        participants = {main_username: {'status': 'accepted'}}
        for friend in invited_friends:
            participants[friend] = {'status': 'invited'}

        new_challenge_data = {
            'creatorUsername': main_username, 'title': title, 'description': description,
            'problems': problems_list, 'expiresAt': expires_at, 'status': 'active',
            'participants': participants
        }
        success = firebase_service.create_challenge(new_challenge_data)

        if success:
            flash("Challenge created successfully! It will become active once a friend accepts.", "success")
            return redirect(url_for('challenges.challenges_page'))
        else:
            flash("There was an error creating the challenge.", "error")
            return redirect(url_for('challenges.create_challenge'))

    friends_list = firebase_service.get_friends(main_username)
    return render_template('create_challenge.html', friends=friends_list)


@bp.route('/challenges/respond/<string:challenge_id>/<string:response>', methods=['POST'])
def respond_to_challenge(challenge_id, response):
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))
    if response in ['accepted', 'declined']:
        firebase_service.update_challenge_participant_status(challenge_id, main_username, response)
        flash(f"You have {response} the challenge!", "success")
    return redirect(url_for('challenges.challenges_page'))


@bp.route('/challenges/delete/<string:challenge_id>', methods=['POST'])
def delete_challenge(challenge_id):
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))
    challenge = firebase_service.get_challenge_by_id(challenge_id)
    if challenge and challenge.get('creatorUsername') == main_username:
        firebase_service.delete_challenge(challenge_id)
        flash("Challenge successfully deleted.", "success")
    else:
        flash("You do not have permission to delete this challenge.", "error")
    return redirect(url_for('challenges.challenges_page'))


@bp.route('/challenges/edit/<string:challenge_id>', methods=['GET', 'POST'])
def edit_challenge(challenge_id):
    main_username = session.get('leetcode_username')
    if not main_username:
        return redirect(url_for('auth.login'))
    challenge = firebase_service.get_challenge_by_id(challenge_id)
    if not challenge or challenge.get('creatorUsername') != main_username:
        flash("You do not have permission to edit this challenge.", "error")
        return redirect(url_for('challenges.challenges_page'))
    if request.method == 'POST':
        updated_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description')
        }
        firebase_service.update_challenge_details(challenge_id, updated_data)
        flash("Challenge details updated successfully.", "success")
        return redirect(url_for('challenges.challenges_page'))
    return render_template('edit_challenge.html', challenge=challenge)