import os
import logging
from flask import Flask
from dotenv import load_dotenv
from .models import db
from .routes import bp
from .functions.database import init_database

##################################################
# 1. Load environment variables & define Config
##################################################
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes"]
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))  # Default port is 5000

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def validate():
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment or .env file.")

##################################################
# 2. Create the Flask application
##################################################
def create_app():
    app = Flask(__name__)

    # Set logging level to INFO
    app.logger.setLevel(logging.INFO)

    # Load configuration
    app.config.from_object(Config)

    # Validate configuration
    Config.validate()

    # Initialize the database
    db.init_app(app)
    init_database(app)

    # Register routes
    app.register_blueprint(bp)

    # Run the app
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=Config.FLASK_PORT)

    return app

##################################################
# 3. Entry point
##################################################
if __name__ == "__main__":
    create_app()
