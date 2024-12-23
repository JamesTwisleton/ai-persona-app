import os
from flask import Flask
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

        # Ensure the data directory exists
        os.makedirs("app/data", exist_ok=True)

        # Create data directory if it doesn't exist
        database_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        db.create_all()

    # # Create database tables
    # with app.app_context():
    
        # db.create_all()

        # Check if data is already populated
        if not AttributeType.query.first():
            print("Populating database with initial data...")
            populate_database_with_initial_data()

    # Register routes    
    app.register_blueprint(bp)            

    return app


def populate_database_with_initial_data():
    """
    Populate the database with initial data.
    This function includes all the data from the `post_archetypes_attributes.sh` script.
    """
    from .models import db

    # Define the initial data for the database
    initial_data = [
        {
            "name": "economic",
            "left_name": "left",
            "right_name": "right",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.1},
                {"name": "The Authoritarian Realist", "value": 0.8},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.3},
                {"name": "The Pragmatic Traditionalist", "value": 0.9},
            ],
        },
        {
            "name": "freedom",
            "left_name": "Authoritarian",
            "right_name": "Libertarian",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.9},
                {"name": "The Authoritarian Realist", "value": 0.1},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.8},
                {"name": "The Pragmatic Traditionalist", "value": 0.3},
            ],
        },
        {
            "name": "tone",
            "left_name": "Negative",
            "right_name": "Positive",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.2},
                {"name": "The Authoritarian Realist", "value": 0.3},
                {"name": "The Diplomatic Centrist", "value": 0.9},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.8},
                {"name": "The Pragmatic Traditionalist", "value": 0.5},
            ],
        },
        {
            "name": "cultural",
            "left_name": "Traditional",
            "right_name": "Progressive",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.9},
                {"name": "The Authoritarian Realist", "value": 0.1},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.9},
                {"name": "The Progressive Idealist", "value": 1.0},
                {"name": "The Pragmatic Traditionalist", "value": 0.2},
            ],
        },
        {
            "name": "conflict",
            "left_name": "Avoidant",
            "right_name": "Confrontational",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.3},
                {"name": "The Authoritarian Realist", "value": 0.8},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.6},
                {"name": "The Pragmatic Traditionalist", "value": 0.4},
            ],
        },
        {
            "name": "optimism",
            "left_name": "Pessimistic",
            "right_name": "Optimistic",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.8},
                {"name": "The Authoritarian Realist", "value": 0.2},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 1.0},
                {"name": "The Pragmatic Traditionalist", "value": 0.4},
            ],
        },
    ]

    # Populate the database with the data
    for attribute_type in initial_data:
        # Create an instance of AttributeType and add it to the database
        attribute_type_instance = AttributeType(
            name=attribute_type["name"],
            left_name=attribute_type["left_name"],
            right_name=attribute_type["right_name"],
        )
        db.session.add(attribute_type_instance)
        db.session.commit()

        # Add the archetypes associated with the current attribute type
        for archetype in attribute_type["archetypes"]:
            archetype_instance = Archetype(
                name=archetype["name"],
                value=archetype["value"],
                attribute_type_id=attribute_type_instance.id,
            )
            db.session.add(archetype_instance)
            db.session.commit()

    print("The database has been populated with all the initial data successfully.")
