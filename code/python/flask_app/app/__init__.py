import os
from flask import Flask
import json
from .models import db, AttributeType, Archetype
from .routes import bp
from .config import Config

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('app.config.Config')

    # Validate configuration
    Config.validate()

    # Initialize database
    db.init_app(app)

    with app.app_context():

        # Ensure the data directory and DB file exist, creating them if they don't
        os.makedirs("app/data", exist_ok=True)
        database_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        
        db.create_all()

        # Check if data is already populated
        if not AttributeType.query.first():
            print("Populating database with initial data...")
            populate_database_with_initial_data()

    # Register routes    
    app.register_blueprint(bp)            

    return app


def populate_database_with_initial_data():
    """
    Populate the database with initial data from archetypes.json.
    """
    # Path to the archetypes.json file
    archetypes_file_path = os.path.join(os.path.dirname(__file__), 'static', 'archetypes', 'archetypes.json')

    try:
        # Load the JSON data from the file
        with open(archetypes_file_path, 'r') as file:
            data = json.load(file)

        # Iterate over each attribute type in the JSON data
        for attribute_type in data.get("AttributeTypes", []):
            # Create an instance of AttributeType and add it to the database
            attribute_type_instance = AttributeType(
                name=attribute_type["name"],
                left_name=attribute_type["left_name"],
                right_name=attribute_type["right_name"]
            )
            db.session.add(attribute_type_instance)
            db.session.commit()

            # Add the archetypes associated with the current attribute type
            for archetype in attribute_type.get("archetypes", []):
                archetype_instance = Archetype(
                    name=archetype["name"],
                    value=archetype["value"],
                    attribute_type_id=attribute_type_instance.id
                )
                db.session.add(archetype_instance)

        # Commit all changes to the database
        db.session.commit()

        print("The database has been populated with data from archetypes.json successfully.")

    except FileNotFoundError:
        print(f"Error: The file {archetypes_file_path} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
