import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the Flask app."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key-for-dev'
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    LEETCODE_API_ENDPOINT = 'https://leetcode.com/graphql'