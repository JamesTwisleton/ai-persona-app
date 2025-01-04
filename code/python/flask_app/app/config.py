from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes"]
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))  # Default port is 5000 if not set

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def validate():
        # Check required variables
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment or .env file.")
