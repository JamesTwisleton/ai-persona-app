import os
from flask import Flask
import json
from .models import db, AttributeType, Archetype, Persona
from .routes import bp
from .config import Config
from datetime import date, datetime

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('app.config.Config')

    # Validate configuration
    Config.validate()

    # Initialize database
    db.init_app(app)

    with app.app_context():
        # Create the database tables
        db.create_all()

        # Check if archetypes are already populated, if not then populate them
        if not AttributeType.query.first():
            print("Populating database with initial archetypes...")
            populate_initial_attribute_types()

        # Check if personas are already populated, if not then populate them
        if not Persona.query.first():
            print("Populating database with initial personas...")
            populate_initial_personas()

    # Register routes    
    app.register_blueprint(bp)            

    return app


def populate_initial_attribute_types():
    """
    Populate the database with initial data from archetypes.json.
    """

    # Load archetypes
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

def populate_initial_personas():
    """
    Populate the database with initial data from personas.json.
    """

    # Load personas
    # Path to the personas.json file
    personas_file_path = os.path.join(os.path.dirname(__file__), 'static', 'personas', 'personas.json')
    current_timestamp = datetime.now().isoformat()

    try:
        # Load the JSON data from the file
        with open(personas_file_path, 'r') as file:
            data = json.load(file)

        # Iterate over each attribute type in the JSON data
        for persona in data.get("Personas", []):
            # Create an instance of AttributeType and add it to the database
            persona_instance = Persona(
                        id=persona["id"],
                        user_id=persona["id"],
                        name=persona["name"],
                        dob=persona["dob"],
                        location=persona["location"],
                        profile_picture_s3_bucket_address=persona["profile_picture_s3_bucket_address"],
                        creation_date=current_timestamp)
            
            db.session.add(persona_instance)

        # Commit all changes to the database
        db.session.commit()

        print("The database has been populated with data from personas.json successfully.")

    except FileNotFoundError:
        print(f"Error: The file {personas_file_path} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
