import json
import os
from datetime import datetime
from flask import Flask, jsonify, Response
from sqlalchemy.orm import joinedload
import uuid

from .utils import calculate_age
from ..models import db, Persona, Conversation, Message, ConversationParticipants, AttributeType, Archetype, Attribute

def init_database(app):
    """
    Create database tables (if they don't exist), then populate with initial data
    if archetypes and/or personas are missing.
    """
    with app.app_context():
        db.create_all()

        # Check if archetypes are already populated, if not then populate them
        if not AttributeType.query.first():
            app.logger.info("Populating database with initial archetypes...")
            populate_initial_attribute_types()

        # Check if personas are already populated, if not then populate them
        if not Persona.query.first():
            app.logger.info("Populating database with initial personas...")
            populate_initial_personas()

def populate_initial_attribute_types():
    """
    Populate the database with initial data from archetypes.json.
    """

    # Load archetypes
    # Path to the archetypes.json file
    # Calculate the correct path relative to the 'app' directory
    archetypes_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'static', 'archetypes', 'archetypes.json'
    )

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
        db.session.rollback()
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
        db.session.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.session.rollback()

def populate_initial_personas():
    """
    Populate the database with initial data from personas.json.
    """

    # Load personas
    personas_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'static', 'personas', 'personas.json'
    )

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
                uuid=str(uuid.uuid4())[:6],
                user_id=persona["id"],
                name=persona["name"],
                dob=persona["dob"],
                location=persona["location"],
                profile_picture_filename=persona["profile_picture_filename"],
                creation_date=current_timestamp
            )
            db.session.add(persona_instance)

            # Add Attributes
            for attr_data in persona.get("attributes", []):
                # Add the Attribute
                attribute = Attribute(
                    persona_id=persona_instance.id,
                    attribute_type_id=attr_data["attribute_type_id"],
                    value=attr_data["value"]
                )
                db.session.add(attribute)

        # Commit all changes to the database
        db.session.commit()
        print("The database has been populated with data from personas.json successfully.")

    except FileNotFoundError:
        print(f"Error: The file {personas_file_path} was not found.")
        db.session.rollback()
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
        db.session.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.session.rollback()

def retrieve_personas_from_database():
    """
    Get all personas from the database.
    """

    app = Flask(__name__)
    # Query all personas
    personas_query = db.session.query(Persona).all()

    # Format the results
    personas_data = []
    for persona in personas_query:
        persona_data = {
            "uuid": persona.uuid,
            "name": persona.name,
            "age": calculate_age(persona.dob),
            "location": persona.location,
            "profile_picture_filename": persona.profile_picture_filename,
            "attributes": []
        }

        # Add attributes for this persona
        for attribute in persona.attributes_relation:
            attribute_data = {
                "id": str(attribute.id),
                "name": attribute.attribute_type_relation.name,
                "value": attribute.value
            }
            persona_data["attributes"].append(attribute_data)

        personas_data.append(persona_data)

    app.logger.info("Personas returned from get-personas: ")
    app.logger.info(personas_data)

    # Use json.dumps to serialize and maintain order
    return Response(json.dumps({"personas": personas_data}, sort_keys=False), mimetype="application/json")

def retrieve_conversations_from_database():
    """
    Get all conversations from the database, including related users, personas, and messages.
    """
    conversations_query = db.session.query(Conversation).options(
        joinedload(Conversation.user_relation),
        joinedload(Conversation.messages_relation).joinedload(Message.persona_relation),
        joinedload(Conversation.conversation_participants_relation).joinedload(ConversationParticipants.persona_relation)
    ).all()

    # Format the results
    conversations_data = []
    for conversation in conversations_query:
        conversation_data = {
            "uuid": conversation.uuid,
            "user_uuid": str(conversation.user_relation.uuid),
            "topic": conversation.topic,
            "created": conversation.created,
            "personas": []
        }
        personas = {str(p.persona_relation.id): p.persona_relation
                    for p in conversation.conversation_participants_relation}
        for message in conversation.messages_relation:
            personas[str(message.persona_relation.id)] = message.persona_relation

        for persona in personas.values():
            persona_data = {
                "uuid": str(persona.uuid),
                "name": persona.name,
                "age": calculate_age(persona.dob),
                "location": persona.location,
                "profile_picture_filename": persona.profile_picture_filename,
                "messages": []
            }

            # Add messages for this persona
            for message in conversation.messages_relation:
                if message.persona_relation.id == persona.id:
                    message_data = {
                        "uuid": str(message.uuid),
                        "content": message.content,
                        "created": message.created
                    }
                    persona_data["messages"].append(message_data)

            conversation_data["personas"].append(persona_data)

        conversations_data.append(conversation_data)

    # Use json.dumps to serialize and maintain order
    return Response(json.dumps({"conversations": conversations_data}, sort_keys=False), mimetype="application/json")
