# ==============================================================================
# Application Factory
# ------------------------------------------------------------------------------
# This file contains the 'create_app' function, which is known as the
# application factory. It's responsible for all application setup.
# ==============================================================================

import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from config import Config
from flask_mail import Mail

# Define the mail object in the global scope. It will be initialized later.
mail = Mail()

def create_app(config_class=Config):
    """
    Application factory function. Configures and returns the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize the mail object with the application instance
    mail.init_app(app)

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        cred_path = app.config['FIREBASE_CREDENTIALS_PATH']
        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS_PATH is not set in the configuration.")
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
        except Exception as e:
            raise ValueError(f"Failed to initialize Firebase Admin SDK: {e}")

    # Store the db client in the app config for easy access
    db_client = firestore.client()
    app.config['DB'] = db_client
    
    # --- Import and Register All Blueprints ---
    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from .routes.friends import bp as social_bp 
    app.register_blueprint(social_bp)
    
    from .routes.challenges import bp as challenges_bp
    app.register_blueprint(challenges_bp)

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app