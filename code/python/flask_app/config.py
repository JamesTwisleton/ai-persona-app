import os

# Remeber to set environment variables from CLI:
#export SECRET_KEY='a_super_secret_value'
#export FLASK_DEBUG=False

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_key')  # Fallback for development only
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'   # Dynamically set DEBUG