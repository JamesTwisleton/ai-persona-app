from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def validate():
        # Check required variables
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment or .env file.")
