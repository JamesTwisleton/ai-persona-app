from flask import Flask, jsonify
from sqlalchemy.orm import joinedload
from ..models import db, Persona, Conversation, Message, ConversationParticipants

app = Flask(__name__)

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
