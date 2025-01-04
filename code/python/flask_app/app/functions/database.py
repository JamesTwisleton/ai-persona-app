import json
import os
from datetime import datetime

from flask import Flask, jsonify
from sqlalchemy.orm import joinedload
from ..models import db, Persona, Conversation, Message, ConversationParticipants, AttributeType, Archetype, Attribute

app = Flask(__name__)

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
        os.path.dirname(os.path.dirname(__file__)),  # Move up one directory to 'app'
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
                user_id=persona["id"],
                name=persona["name"],
                dob=persona["dob"],
                location=persona["location"],
                profile_picture_s3_bucket_address=persona["profile_picture_s3_bucket_address"],
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
    # Query all personas
    personas_query = db.session.query(Persona).all()

    # Format the results
    personas_data = []
    for persona in personas_query:
        persona_data = {
            "id": str(persona.id),
            "name": persona.name,
            "dob": persona.dob,
            "location": persona.location,
            "profile_picture_s3_bucket_address": persona.profile_picture_s3_bucket_address,
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

    # Return as JSON
    app.logger.info("Personas returned from get-personas: ", personas_data)
    return jsonify({"personas": personas_data})

def retrieve_conversations_from_database():
    # Query conversations, including related users, personas, and messages
    conversations_query = db.session.query(Conversation).options(
        joinedload(Conversation.user_relation),  # Include the related user
        joinedload(Conversation.messages_relation).joinedload(Message.persona_relation),  # Include messages and their related personas
        joinedload(Conversation.conversation_participants_relation).joinedload(ConversationParticipants.persona_relation)  # Include conversation participants (personas)
    ).all()

    # Format the results
    conversations_data = []
    for conversation in conversations_query:
        conversation_data = {
            "conversation_id": str(conversation.id),  # You can replace this with UUID if your ID is UUID
            "user_id": str(conversation.user_relation.id),  # Replace with the user_id
            "topic": conversation.topic,
            "created": conversation.created,
            "personas": []
        }

        # Process personas for the conversation (both participants and those who sent messages)
        personas = {str(participant.persona_relation.id): participant.persona_relation for participant in conversation.conversation_participants_relation}
        
        # Add personas from messages as well
        for message in conversation.messages_relation:
            personas[str(message.persona_relation.id)] = message.persona_relation

        for persona in personas.values():
            persona_data = {
                "id": str(persona.id),
                "name": persona.name,
                "dob": persona.dob,
                "location": persona.location,
                "profile_picture_s3_bucket_address": persona.profile_picture_s3_bucket_address,
                "messages": []
            }

            # Add messages for this persona
            for message in conversation.messages_relation:
                if message.persona_relation.id == persona.id:
                    message_data = {
                        "id": str(message.id),
                        "content": message.content,
                        "created": message.created
                    }
                    persona_data["messages"].append(message_data)

            conversation_data["personas"].append(persona_data)

        conversations_data.append(conversation_data)

    # Return as JSON
    return jsonify({"conversations": conversations_data})
