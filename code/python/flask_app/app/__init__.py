from flask import Flask
from .config import Config
from .routes import bp as route_bp
from .models import db
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(route_bp)

    # Initialize database tables
    with app.app_context():
        db.init_app(app)
        db.create_all() # Already here

    return app
