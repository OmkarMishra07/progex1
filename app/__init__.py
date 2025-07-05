import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from config import Config

# This will hold the Firestore client
db = None

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    global db
    # Initialize Firebase Admin SDK only if it hasn't been already
    if not firebase_admin._apps:
        cred_path = app.config['FIREBASE_CREDENTIALS_PATH']
        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS_PATH is not set.")
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
        except Exception as e:
            raise ValueError(f"Failed to initialize Firebase Admin SDK: {e}")

    db = firestore.client()

    # Import and register blueprints
    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from .routes.friends import bp as friends_bp
    app.register_blueprint(friends_bp)
    
    from .routes.challenges import bp as challenges_bp
    app.register_blueprint(challenges_bp)

    return app