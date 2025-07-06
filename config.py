import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the root directory
load_dotenv()

class Config:
    """
    Configuration settings for the Flask app.
    It reads sensitive values from environment variables for security.
    """
    # --- Core Flask & Application Settings ---
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # --- Service Credentials & Endpoints ---
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    LEETCODE_API_ENDPOINT = 'https://leetcode.com/graphql'

    # --- Email Configuration ---
    # This section is configured to handle both SSL and TLS connections,
    # with SSL being the preferred method for the current troubleshooting step.
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    
    # Check for MAIL_USE_SSL first. This should be 'True' for port 465.
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    
    # Only use TLS if SSL is not being used. This prevents conflicts.
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None and not MAIL_USE_SSL
    
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Enable verbose debug output for Flask-Mail. This is crucial for diagnostics.
    MAIL_DEBUG = True