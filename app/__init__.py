# ==============================================================================
# Application Factory
# ------------------------------------------------------------------------------
# This file contains the 'create_app' function, which is known as the
# application factory. It's responsible for:
#   - Creating the Flask application instance.
#   - Loading configuration from the config.py file.
#   - Initializing extensions like Flask-Mail and the Firebase Admin SDK.
#   - Storing the database client in the app's config for easy access.
#   - Registering all the feature blueprints (routes).
# ==============================================================================

import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from config import Config
from flask_mail import Mail

# Create an instance of the Flask-Mail extension, but don't configure it yet.
mail = Mail()

def create_app(config_class=Config):
    """
    Application factory function. Configures and returns the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the application instance
    mail.init_app(app)

    # Initialize Firebase Admin SDK only if it hasn't been initialized already.
    # This prevents errors during hot-reloading in development.
    if not firebase_admin._apps:
        cred_path = app.config['FIREBASE_CREDENTIALS_PATH']
        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS_PATH is not set in the configuration.")
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
        except Exception as e:
            # Provide a clear error message if Firebase fails to initialize.
            raise ValueError(f"Failed to initialize Firebase Admin SDK: {e}")

    # Get the Firestore client and store it in the app's config.
    # This is the standard way to make it accessible throughout the application
    # via Flask's `current_app` proxy.
    db_client = firestore.client()
    app.config['DB'] = db_client
    
    # Import and register all the blueprints from the 'routes' package
    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from .routes.friends import bp as friends_bp
    app.register_blueprint(friends_bp)
    
    from .routes.challenges import bp as challenges_bp
    app.register_blueprint(challenges_bp)

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app