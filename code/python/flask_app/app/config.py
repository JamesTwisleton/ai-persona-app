import os

# Remember to set environment variables from CLI:
#export SECRET_KEY='a_super_secret_value'
#export FLASK_DEBUG=False

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_key')  # Fallback for development only
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'   # Dynamically set DEBUG
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")