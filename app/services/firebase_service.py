# app/services/firebase_service.py

from flask import current_app
from firebase_admin import firestore
import datetime

# This helper function makes the code cleaner by getting the db connection
# from the current application context.
def _get_db():
    """Returns the Firestore client from the current Flask app's config."""
    return current_app.config['DB']

def get_user_data(username):
    """Fetches a user's document from the 'users' collection in Firestore."""
    if not username:
        return None
    db = _get_db()
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def get_user_by_email(email):
    """Finds a user document by their email address."""
    db = _get_db()
    users_ref = db.collection('users').where('email', '==', email).limit(1)
    docs = users_ref.stream()
    for doc in docs:
        return doc.to_dict()
    return None

def add_or_update_user(username):
    """Creates a user document if it doesn't exist."""
    if not username:
        return False
    db = _get_db()
    user_ref = db.collection('users').document(username)
    user_ref.set({'leetcode_username': username}, merge=True)
    return True

def create_unverified_user(username, email, otp):
    """Creates a user with an OTP, but not yet verified."""
    db = _get_db() # <--- THIS IS ONE OF THE LINES THAT WAS FIXED
    user_ref = db.collection('users').document(username)
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    
    user_ref.set({
        'leetcode_username': username,
        'email': email,
        'is_verified': False,
        'otp': otp,
        'otp_expires': expiration
    })

def verify_user_and_set_password(username, password_hash):
    """Sets the user's password hash and marks them as verified."""
    db = _get_db()
    user_ref = db.collection('users').document(username)
    user_ref.update({
        'password_hash': password_hash,
        'is_verified': True,
        'otp': firestore.DELETE_FIELD,
        'otp_expires': firestore.DELETE_FIELD
    })

def add_friend(main_username, friend_username):
    """Adds a friend's username to a user's friend list array."""
    if not main_username or not friend_username or main_username == friend_username:
        return False
    db = _get_db()
    user_ref = db.collection('users').document(main_username)
    user_ref.update({
        'friends': firestore.ArrayUnion([friend_username])
    })
    return True

def remove_friend(main_username, friend_username):
    """Removes a friend from a user's friend list."""
    if not main_username or not friend_username:
        return False
    db = _get_db()
    user_ref = db.collection('users').document(main_username)
    user_ref.update({
        'friends': firestore.ArrayRemove([friend_username])
    })
    return True
# app/services/firebase_service.py
# ... (add these two new functions) ...

def set_password_reset_otp(username, otp):
    """Sets a temporary OTP for password reset."""
    user_ref = db.collection('users').document(username)
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    
    user_ref.update({
        'reset_otp': otp,
        'reset_otp_expires': expiration
    })

def reset_password(username, new_password_hash):
    """Updates the user's password and removes the reset OTP."""
    user_ref = db.collection('users').document(username)
    user_ref.update({
        'password_hash': new_password_hash,
        'reset_otp': firestore.DELETE_FIELD,
        'reset_otp_expires': firestore.DELETE_FIELD
    })

def get_friends(main_username):
    """Retrieves the list of friends for a user."""
    user_data = get_user_data(main_username)
    return user_data.get('friends', []) if user_data else []

def get_active_challenges():
    """Fetches all documents from the 'challenges' collection where isActive is true."""
    db = _get_db()
    challenges_ref = db.collection('challenges').where('isActive', '==', True)
    docs = challenges_ref.stream()
    
    challenges = []
    for doc in docs:
        challenge_data = doc.to_dict()
        challenge_data['id'] = doc.id
        challenges.append(challenge_data)
        
    return challenges