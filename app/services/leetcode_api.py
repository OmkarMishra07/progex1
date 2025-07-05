import httpx
from flask import current_app

# ==============================================================================
# LeetCode API Service
# ------------------------------------------------------------------------------
# This file contains all the functions needed to communicate with the
# official LeetCode GraphQL API. It uses the httpx library for making
# synchronous HTTP requests, which is a modern and robust alternative
# to the 'requests' library.
#
# Key Components:
#   - _send_graphql_request: A private helper function that handles the logic
#     for sending a POST request to the GraphQL endpoint.
#
#   - Public Functions (get_user_stats, etc.): Each function is responsible
#     for fetching a specific piece of data. They define their own GraphQL
#     query and format the response for easy use in the Flask routes.
# ==============================================================================


def _send_graphql_request(query, variables):
    """
    A private helper function to send GraphQL requests to LeetCode's API.

    Args:
        query (str): The GraphQL query string.
        variables (dict): A dictionary of variables to pass with the query.

    Returns:
        dict: The 'data' part of the JSON response, or None if an error occurs.
    """
    url = current_app.config['LEETCODE_API_ENDPOINT']
    
    json_payload = {
        "query": query,
        "variables": variables
    }

    try:
        # Use a synchronous httpx.Client for making the request in a Flask context
        with httpx.Client() as client:
            # Set a reasonable timeout to prevent hanging requests
            response = client.post(url, json=json_payload, timeout=20.0)
            # Raise an exception for HTTP errors like 404 or 500
            response.raise_for_status()
            
            data = response.json()
            # The LeetCode API can return errors in the JSON body even with a 200 status
            if "errors" in data:
                print(f"GraphQL Error received from LeetCode API: {data['errors']}")
                return None
            return data.get('data')

    except httpx.RequestError as e:
        # Handles network-related errors (DNS issues, connection refused, etc.)
        print(f"An HTTPX network error occurred: {e}")
        return None
    except Exception as e:
        # Handles other potential errors (e.g., JSON decoding issues)
        print(f"An unexpected error occurred in the API service: {e}")
        return None


def get_user_stats(username):
    """
    Fetches a user's profile stats and current streak from LeetCode.
    This function makes TWO separate API calls and combines the results.
    """
    # --- Part 1: Get Solved Problem Counts and Avatar ---
    stats_query = """
    query userPublicProfile($username: String!) {
        matchedUser(username: $username) {
            username
            profile {
                userAvatar
            }
            submitStats: submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    stats_variables = {"username": username}
    stats_data = _send_graphql_request(stats_query, stats_variables)

    # If the user doesn't exist or the first API call fails, stop and return None.
    if not stats_data or not stats_data.get('matchedUser'):
        return None

    user_data = stats_data['matchedUser']
    stats = user_data['submitStats']['acSubmissionNum']
    
    # Prepare the initial stats dictionary from the first API call's data
    formatted_stats = {
        'username': user_data['username'],
        'avatar': user_data['profile']['userAvatar'],
        'totalSolved': next((s['count'] for s in stats if s['difficulty'] == 'All'), 0),
        'easySolved': next((s['count'] for s in stats if s['difficulty'] == 'Easy'), 0),
        'mediumSolved': next((s['count'] for s in stats if s['difficulty'] == 'Medium'), 0),
        'hardSolved': next((s['count'] for s in stats if s['difficulty'] == 'Hard'), 0),
        'streak': 0  # Default streak to 0 before the second API call
    }

    # --- Part 2: Get the Current Streak from the User's Calendar ---
    streak_query = """
    query userDailyCodingChallenge($username: String!) {
        matchedUser(username: $username) {
            userCalendar {
                streak
                totalActiveDays
            }
        }
    }
    """
    streak_variables = {"username": username}
    streak_data = _send_graphql_request(streak_query, streak_variables)

    # If the streak data was fetched successfully, update the dictionary
    if streak_data and streak_data.get('matchedUser') and streak_data['matchedUser'].get('userCalendar'):
        formatted_stats['streak'] = streak_data['matchedUser']['userCalendar']['streak']

    # --- Part 3: Return the final, combined data ---
    return formatted_stats


def get_recent_submissions(username, limit=10):
    """
    Fetches a user's most recent submissions from LeetCode.
    """
    query = """
    query recentSubmissions($username: String!, $limit: Int!) {
        recentSubmissionList(username: $username, limit: $limit) {
            title
            titleSlug
            timestamp
            statusDisplay
            lang
        }
    }
    """
    variables = {"username": username, "limit": limit}
    data = _send_graphql_request(query, variables)

    if data and data.get('recentSubmissionList'):
        return data['recentSubmissionList']
    
    return [] # Return an empty list if no data is found


def get_daily_challenge():
    """
    Fetches the current daily coding challenge from LeetCode.
    """
    query = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            link
            question {
                questionId
                questionFrontendId
                title
                titleSlug
                difficulty
            }
        }
    }
    """
    variables = {}
    data = _send_graphql_request(query, variables)

    if data and data.get('activeDailyCodingChallengeQuestion'):
        challenge_data = data['activeDailyCodingChallengeQuestion']
        # Format the data into a simple dictionary for the template
        return {
            'title': challenge_data['question']['title'],
            'difficulty': challenge_data['question']['difficulty'],
            # The API returns a relative URL, so we must prepend the domain
            'link': f"https://leetcode.com{challenge_data['link']}"
        }

    return None # Return None if the daily challenge can't be fetched