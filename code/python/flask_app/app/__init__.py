from flask import Flask
import logging
from .models import db, AttributeType, Persona
from .routes import bp
from .config import Config
from .functions.database import populate_initial_attribute_types, populate_initial_personas

def create_app():
    app = Flask(__name__)

    # Set logging level to INFO
    app.logger.setLevel(logging.INFO)

    # Load configuration
    app.config.from_object('app.config.Config')

    # Validate configuration
    Config.validate()

    # Set up the DB
    db.init_app(app)

    with app.app_context():
        # Create the database tables
        db.create_all()

        # Check if archetypes are already populated, if not then populate them
        if not AttributeType.query.first():
            app.logger.info("Populating database with initial archetypes...")
            populate_initial_attribute_types()

        # Check if personas are already populated, if not then populate them
        if not Persona.query.first():
            app.logger.info("Populating database with initial personas...")
            populate_initial_personas()

    # Register routes    
    app.register_blueprint(bp)

    debug_mode = Config.DEBUG
    port = Config.FLASK_PORT
    app.run(debug=debug_mode, host="0.0.0.0", port=port)

    return app

# Entry point
if __name__ == "__main__":
    create_app()
