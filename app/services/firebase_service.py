# ==============================================================================
# Firebase Database Service
# ------------------------------------------------------------------------------
# This file handles all communication with the Google Firestore database.
# It's responsible for all CRUD (Create, Read, Update, Delete) operations
# related to users and their friends.
# ==============================================================================

# This import makes the database connection object ('db') available in this file.
from app import db

from firebase_admin import firestore

def get_user_data(username):
    """
    Fetches a user's document from the 'users' collection in Firestore.

    Args:
        username (str): The LeetCode username, which is used as the document ID.

    Returns:
        dict: The user's data as a dictionary, or None if not found.
    """
    if not username:
        return None
    doc_ref = db.collection('users').document(username)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def add_or_update_user(username):
    """
    Creates a user document if it doesn't exist. This ensures that every
    user who logs in has an entry in our database.
    """
    if not username:
        return False
    user_ref = db.collection('users').document(username)
    # Using set with merge=True creates the doc or updates it without overwriting
    # other fields like the 'friends' array.
    user_ref.set({'leetcode_username': username}, merge=True)
    return True

def add_friend(main_username, friend_username):
    """
    Adds a friend's username to a user's friend list array in Firestore.
    It prevents adding yourself or duplicate entries.
    """
    if not main_username or not friend_username or main_username == friend_username:
        return False
    user_ref = db.collection('users').document(main_username)
    # ArrayUnion is an atomic operation that adds an element to an array
    # only if it doesn't already exist.
    user_ref.update({
        'friends': firestore.ArrayUnion([friend_username])
    })
    return True

def remove_friend(main_username, friend_username):
    """
    Removes a friend from a user's friend list in Firestore.
    """
    if not main_username or not friend_username:
        return False
    user_ref = db.collection('users').document(main_username)
    # ArrayRemove is an atomic operation that removes all instances of the
    # given element from an array.
    user_ref.update({
        'friends': firestore.ArrayRemove([friend_username])
    })
    return True

def get_friends(main_username):
    """
    Retrieves the list of friends (usernames) for a given user.
    """
    user_data = get_user_data(main_username)
    # Safely get the 'friends' list. If the user doesn't exist or has no friends,
    # it returns an empty list, preventing errors.
    return user_data.get('friends', []) if user_data else []