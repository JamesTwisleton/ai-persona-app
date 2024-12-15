import os

# Remember to set in .env file
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'   # Dynamically set DEBUG