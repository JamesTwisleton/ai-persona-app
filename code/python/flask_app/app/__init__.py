from flask import Flask
import logging
from .models import db
from .routes import bp
from .config import Config
from .functions.database import init_database

def create_app():
    app = Flask(__name__)

    # Set logging level to INFO
    app.logger.setLevel(logging.INFO)

    # Load configuration
    app.config.from_object('app.config.Config')

    # Validate configuration
    Config.validate()

    # Set up the DB (SQLAlchemy)
    db.init_app(app)

    # Initialize the DB (create tables & populate if needed)
    init_database(app)

    # Register routes
    app.register_blueprint(bp)

    debug_mode = Config.DEBUG
    port = Config.FLASK_PORT

    # Run the app
    app.run(debug=debug_mode, host="0.0.0.0", port=port)

    return app

# Entry point
if __name__ == "__main__":
    create_app()
