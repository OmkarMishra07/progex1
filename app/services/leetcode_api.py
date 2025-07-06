import httpx
from flask import current_app

def _send_graphql_request(query, variables):
    url = current_app.config['LEETCODE_API_ENDPOINT']
    json_payload = {"query": query, "variables": variables}
    try:
        with httpx.Client() as client:
            response = client.post(url, json=json_payload, timeout=20.0)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                print(f"GraphQL Error: {data['errors']}")
                return None
            return data.get('data')
    except Exception as e:
        print(f"API Service Error: {e}")
        return None

def get_user_stats(username):
    stats_query = """
    query userPublicProfile($username: String!) {
        matchedUser(username: $username) {
            username
            profile { userAvatar ranking }
            submitStats: submitStatsGlobal { acSubmissionNum { difficulty count } }
        }
    }
    """
    stats_data = _send_graphql_request(stats_query, {"username": username})
    if not stats_data or not stats_data.get('matchedUser'):
        return None

    user_data = stats_data['matchedUser']
    stats = user_data['submitStats']['acSubmissionNum']
    formatted_stats = {
        'username': user_data['username'], 'avatar': user_data['profile']['userAvatar'],
        'totalSolved': next((s['count'] for s in stats if s['difficulty'] == 'All'), 0),
        'easySolved': next((s['count'] for s in stats if s['difficulty'] == 'Easy'), 0),
        'mediumSolved': next((s['count'] for s in stats if s['difficulty'] == 'Medium'), 0),
        'hardSolved': next((s['count'] for s in stats if s['difficulty'] == 'Hard'), 0),
    }

    if user_data['profile']['ranking'] and user_data['profile']['ranking'] > 0:
        formatted_stats['globalRanking'] = f"{user_data['profile']['ranking']:,}"
    else:
        formatted_stats['globalRanking'] = "N/A"

    streak_query = """
    query userDailyCodingChallenge($username: String!) {
        matchedUser(username: $username) { userCalendar { streak } }
    }
    """
    streak_data = _send_graphql_request(streak_query, {"username": username})
    formatted_stats['streak'] = streak_data['matchedUser']['userCalendar']['streak'] if streak_data and streak_data.get('matchedUser') and streak_data['matchedUser'].get('userCalendar') else 0
    return formatted_stats

def get_recent_submissions(username, limit=10):
    query = """
    query recentSubmissions($username: String!, $limit: Int!) {
        recentSubmissionList(username: $username, limit: $limit) {
            title titleSlug timestamp statusDisplay lang
        }
    }
    """
    data = _send_graphql_request(query, {"username": username, "limit": limit})
    return data.get('recentSubmissionList', []) if data else []

def get_daily_challenge():
    query = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            link
            question { title titleSlug difficulty }
        }
    }
    """
    data = _send_graphql_request(query, {})
    if data and data.get('activeDailyCodingChallengeQuestion'):
        challenge_data = data['activeDailyCodingChallengeQuestion']
        return {
            'title': challenge_data['question']['title'],
            'difficulty': challenge_data['question']['difficulty'],
            'link': f"https://leetcode.com{challenge_data['link']}"
        }
    return None