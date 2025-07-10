# ==============================================================================
# Firebase Database Service
# ------------------------------------------------------------------------------
# This file handles all communication with the Google Firestore database.
# This version includes the new, automatic seeder for the NeetCode 150 plan.
# ==============================================================================

from flask import current_app
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from werkzeug.security import generate_password_hash
import datetime

# This helper function makes the code cleaner by getting the db connection
def _get_db():
    return current_app.config['DB']

# --- User & Authentication Functions ---
def get_user_data(username):
    if not username: return None
    db = _get_db()
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def get_user_by_email(email):
    db = _get_db()
    users_ref = db.collection('users').where(filter=FieldFilter('email', '==', email)).limit(1)
    docs = users_ref.stream()
    for doc in docs:
        return doc.to_dict()
    return None

def create_unverified_user(username, email, otp):
    db = _get_db()
    user_ref = db.collection('users').document(username)
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    user_ref.set({
        'leetcode_username': username, 'email': email, 'is_verified': False,
        'otp': otp, 'otp_expires': expiration
    })

def verify_user_and_set_password(username, password_hash):
    db = _get_db()
    user_ref = db.collection('users').document(username)
    user_ref.update({
        'password_hash': password_hash, 'is_verified': True,
        'otp': firestore.DELETE_FIELD, 'otp_expires': firestore.DELETE_FIELD
    })

def set_password_reset_otp(username, otp):
    db = _get_db()
    user_ref = db.collection('users').document(username)
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    user_ref.update({'reset_otp': otp, 'reset_otp_expires': expiration})

def reset_password(username, new_password_hash):
    db = _get_db()
    user_ref = db.collection('users').document(username)
    user_ref.update({
        'password_hash': new_password_hash,
        'reset_otp': firestore.DELETE_FIELD, 'reset_otp_expires': firestore.DELETE_FIELD
    })

def delete_user_account(username):
    db = _get_db()
    try:
        db.collection('users').document(username).delete()
        return True
    except Exception as e:
        print(f"Error deleting user {username}: {e}")
        return False

# --- Friends Functions ---
def add_friend(main_username, friend_username):
    if not main_username or not friend_username or main_username == friend_username: return False
    db = _get_db()
    user_ref = db.collection('users').document(main_username)
    user_ref.update({'friends': firestore.ArrayUnion([friend_username])})
    return True

def remove_friend(main_username, friend_username):
    if not main_username or not friend_username: return False
    db = _get_db()
    user_ref = db.collection('users').document(main_username)
    user_ref.update({'friends': firestore.ArrayRemove([friend_username])})
    return True

def get_friends(main_username):
    user_data = get_user_data(main_username)
    return user_data.get('friends', []) if user_data else []


# --- Challenge Functions ---
def create_challenge(challenge_data):
    db = _get_db()
    try:
        db.collection('challenges').add(challenge_data)
        return True
    except Exception as e:
        print(f"Error creating challenge: {e}")
        return False

def get_user_challenges(username):
    db = _get_db()
    challenges_ref = db.collection('challenges').where(filter=FieldFilter('status', '==', 'active'))
    docs = challenges_ref.stream()
    user_challenges = []
    for doc in docs:
        challenge_data = doc.to_dict()
        if username in challenge_data.get('participants', {}):
            challenge_data['id'] = doc.id
            user_challenges.append(challenge_data)
    return user_challenges

def update_challenge_participant_status(challenge_id, username, new_status):
    db = _get_db()
    challenge_ref = db.collection('challenges').document(challenge_id)
    challenge_ref.update({f'participants.{username}.status': new_status})
    return True

def delete_challenge(challenge_id):
    db = _get_db()
    try:
        db.collection('challenges').document(challenge_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting challenge {challenge_id}: {e}")
        return False

def get_challenge_by_id(challenge_id):
    db = _get_db()
    doc = db.collection('challenges').document(challenge_id).get()
    if doc.exists:
        challenge_data = doc.to_dict()
        challenge_data['id'] = doc.id
        return challenge_data
    return None

def update_challenge_details(challenge_id, updated_data):
    db = _get_db()
    try:
        db.collection('challenges').document(challenge_id).update(updated_data)
        return True
    except Exception as e:
        print(f"Error updating challenge {challenge_id}: {e}")
        return False

# --- Study Plan Functions ---
def get_study_plan_questions():
    """Fetches the entire list of curated study plan questions, ordered correctly."""
    db = _get_db()
    docs = db.collection('study_plan_questions').order_by('order').stream()
    return [doc.to_dict() for doc in docs]

def get_or_initialize_user_study_plan(username):
    """Gets a user's study plan progress. If it doesn't exist, creates it."""
    db = _get_db()
    user_ref = db.collection('users').document(username)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        if 'study_plan_progress' in user_data:
            return user_data['study_plan_progress']
        else:
            initial_progress = {'current_question_index': 0}
            user_ref.update({'study_plan_progress': initial_progress})
            return initial_progress
    return None

def advance_user_study_plan(username, current_index):
    """Increments the user's current question index by 1."""
    db = _get_db()
    user_ref = db.collection('users').document(username)
    user_ref.update({'study_plan_progress.current_question_index': firestore.Increment(1)})
    return True

# --- Database Seeder ---
def _create_seed_user(username, email, password):
    db = _get_db()
    password_hash = generate_password_hash(password)
    db.collection('users').document(username).set({
        'leetcode_username': username, 'email': email,
        'password_hash': password_hash, 'is_verified': True, 'friends': []
    })

def seed_database():
    db = _get_db()
    if db.collection('users').document('testuser1').get().exists:
        return "Database has already been seeded. No action taken."
    try:
        _create_seed_user('testuser1', 'testuser1@example.com', 'password123')
        _create_seed_user('testuser2', 'testuser2@example.com', 'password123')
        db.collection('users').document('testuser1').update({'friends': firestore.ArrayUnion(['testuser2'])})
        db.collection('users').document('testuser2').update({'friends': firestore.ArrayUnion(['testuser1'])})
        challenge1_data = {
            'creatorUsername': 'testuser2', 'title': 'Sample Invitation',
            'description': 'A test challenge for testuser1.',
            'expiresAt': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3),
            'status': 'active', 'problems': [{'title': 'Two Sum', 'titleSlug': 'two-sum'}],
            'participants': {'testuser2': {'status': 'accepted'}, 'testuser1': {'status': 'invited'}}
        }
        db.collection('challenges').add(challenge1_data)
        return "Database seeded successfully!"
    except Exception as e:
        return f"An error occurred during seeding: {e}"

# --- NEW: NeetCode 150 Data & Seeder Function ---
NEETCODE_150_QUESTIONS = [
    # A small sample of the NeetCode 150 list.
    # You can expand this list to include all 150 problems.
    {'order': 1, 'topic': 'Arrays & Hashing', 'title': 'Contains Duplicate', 'titleSlug': 'contains-duplicate', 'difficulty': 'Easy', 'videoSolution': 'https://www.youtube.com/watch?v=3OamzN90kPg'},
    {'order': 2, 'topic': 'Arrays & Hashing', 'title': 'Valid Anagram', 'titleSlug': 'valid-anagram', 'difficulty': 'Easy', 'videoSolution': 'https://www.youtube.com/watch?v=9UtInBqnCgA'},
    {'order': 3, 'topic': 'Arrays & Hashing', 'title': 'Two Sum', 'titleSlug': 'two-sum', 'difficulty': 'Easy', 'videoSolution': 'https://www.youtube.com/watch?v=KLlXCFG5TnA'},
    {'order': 4, 'topic': 'Arrays & Hashing', 'title': 'Group Anagrams', 'titleSlug': 'group-anagrams', 'difficulty': 'Medium', 'videoSolution': 'https://www.youtube.com/watch?v=vzdNOK2oB2E'},
    {'order': 5, 'topic': 'Two Pointers', 'title': 'Valid Palindrome', 'titleSlug': 'valid-palindrome', 'difficulty': 'Easy', 'videoSolution': 'https://www.youtube.com/watch?v=jJXJ16kPFWg'},
    {'order': 6, 'topic': 'Two Pointers', 'title': 'Two Sum II - Input Array Is Sorted', 'titleSlug': 'two-sum-ii-input-array-is-sorted', 'difficulty': 'Medium', 'videoSolution': 'https://www.youtube.com/watch?v=cQ1Oz4ckceM'},
    {'order': 7, 'topic': 'Two Pointers', 'title': '3Sum', 'titleSlug': '3sum', 'difficulty': 'Medium', 'videoSolution': 'https://www.youtube.com/watch?v=jzZfxsIWhSc'},
]

def seed_neetcode_plan():
    """
    Automatically populates the `study_plan_questions` collection with the
    NeetCode list. It is idempotent and will not add duplicates.
    """
    db = _get_db()
    collection_ref = db.collection('study_plan_questions')
    
    # Check if the collection is already populated
    if len(list(collection_ref.limit(1).stream())) > 0:
        return "The NeetCode study plan has already been seeded."
        
    try:
        print("Seeding: Populating NeetCode study plan...")
        batch = db.batch()
        for question in NEETCODE_150_QUESTIONS:
            doc_id = f"q{question['order']}"
            doc_ref = collection_ref.document(doc_id)
            batch.set(doc_ref, question)
        
        batch.commit()
        return f"Successfully seeded {len(NEETCODE_150_QUESTIONS)} NeetCode questions!"

    except Exception as e:
        print(f"ERROR during NeetCode seeding: {e}")
        return f"An error occurred during NeetCode seeding: {e}"