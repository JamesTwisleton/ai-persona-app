from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{os.path.join(BASE_DIR, 'data', 'database.db')}"
    )
    # SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    @staticmethod
    def validate():
        # Check required variables
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment or .env file.")
