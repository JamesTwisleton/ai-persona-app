import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from .services.openai_service import generate_character_motto
from .services.huggingface_service import toxicity_classification
from .utils import read_json, get_archetype_as_list, PersonaSpace
from .models import User, Persona, AttributeType, Attribute, Archetype, Conversation, Message, ConversationParticipants


# Global variables
bp = Blueprint("routes", __name__)
PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'static', 'preprompts', 'preprompt_v_0.1.json')
PRE_PROMPT = read_json(PROMPT_PATH)

# Home route
@bp.route("/", methods=["GET"])
def home_route():
    """
    Home endpoint to display a welcome message.
    """
    return "Welcome to my Flask app", 200

# Route to populate initial attributes and archetypes
@bp.route('/populate_attributes_and_archetypes', methods=['POST', 'GET'])
def populate_attributes_and_archetypes():

    from .models import db

    data = request.json
    for attribute_type in data["AttributeTypes"]:
        attribute_type_instance = AttributeType(
            name=attribute_type['name'],
            left_name=attribute_type['left_name'],
            right_name=attribute_type['right_name']
        )
        db.session.add(attribute_type_instance)
        db.session.commit()

        for archetype in attribute_type["archetypes"]:
            archetype_instance = Archetype(
                name=archetype['name'],
                value=archetype['value'],
                attribute_type_id=attribute_type_instance.id
            )
            db.session.add(archetype_instance)
            db.session.commit()

    return jsonify({'status': 'success', 'message': 'Data created successfully!'}), 201

# Route to initialize conversations objects
@bp.route('/init-conversations', methods=['POST', 'GET'])
def init_conversations():

    from .models import db

    current_timestamp = datetime.now().isoformat()
    data = request.get_json()

    if not data or 'conversations' not in data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        for conversation_data in data.get("conversations", []):
            print(conversation_data["topic"])

            # Extract the user
            user_data = conversation_data.get("user", {})

            # Add the User
            user = User.query.filter_by(id=user_data["id"]).first()
            if not user:
                user = User(
                    id=user_data["id"],
                    username=user_data["username"],
                    creation_date=current_timestamp)
                db.session.add(user)

            # Add the Conversation (based on user and conversation ID)
            conversation = Conversation.query.filter_by(id=conversation_data["id"], user_id=user.id).first()
            if not conversation:
                conversation = Conversation(
                    id=conversation_data["id"],
                    topic=conversation_data["topic"],
                    created=current_timestamp,
                    user_id=user.id)
                db.session.add(conversation)
            else:
                # Update conversation fields if necessary
                conversation.topic = conversation_data["topic"]
                conversation.created = current_timestamp

            # Iterate through the Personas
            generated_messages = []
            for persona_data in conversation_data.get("personas", []):
                persona = Persona.query.filter_by(id=persona_data["id"]).first()

                if not persona:
                    # Add the Persona
                    persona = Persona(
                        id=persona_data["id"],
                        user_id=user_data["id"],
                        name=persona_data["name"],
                        dob=persona_data["dob"],
                        location=persona_data["location"],
                        profile_picture_s3_bucket_address=persona_data["profile_picture_s3_bucket_address"],
                        creation_date=current_timestamp)
                    db.session.add(persona)

                # Add Attributes
                for attr_data in persona_data.get("attributes", []):
                    
                    # Grab the persona attributes
                    persona_vector = {attr_data['name']: attr_data['value'] for attr_data in persona_data['attributes']}
                    archetype_attributes = get_archetype_as_list(db)

                    # Initialize the persona space and calculate cosine similarity
                    persona_space = PersonaSpace(persona_vector, archetype_attributes)
                    persona_affinities = persona_space.calculate_similarity()

                    # Modify the pre-prompt based on the persona affinities
                    pre_prompt = PRE_PROMPT
                    pre_prompt['persona']['affinities'] = persona_affinities

                    # Check that the attribute type exists
                    attribute_type_id = attr_data["attribute_type_id"]
                    attribute = Attribute.query.filter_by(
                        persona_id=persona.id, attribute_type_id=attribute_type_id
                    ).first()

                    if not attribute:
                        # Add the Attribute
                        attribute = Attribute(
                            persona_id=persona.id,
                            attribute_type_id=attribute_type_id,
                            value=attr_data["value"])
                        db.session.add(attribute)

                # Contact OPENAI to generate message
                generated_message = generate_character_motto(PRE_PROMPT, conversation_data["topic"])
                print(generated_message)

                # Compute the message toxicity
                toxicity = toxicity_classification([generated_message])
                print(f"Message Toxicity: {toxicity}%", flush=True)
                
                # Check if the persona is already part of this conversation
                conversation_participant = ConversationParticipants.query.filter_by(
                    conversation_id=conversation.id,
                    persona_id=persona.id
                ).first()
                
                # If the persona is not already part of the conversation, add them
                if not conversation_participant:
                    conversation_participant = ConversationParticipants(
                        conversation_id=conversation.id,
                        persona_id=persona.id,
                        role="participant",
                    )
                    db.session.add(conversation_participant)
            
                # Assess message existence
                message = Message.query.filter_by(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    persona_id=persona.id).first()
                
                if not message:
                    message = Message(
                        persona_id=persona.id,
                        content=generated_message,
                        toxicity=toxicity,
                        created=current_timestamp,
                        user_id=user.id,
                        conversation_id=conversation.id)
                
                    # Add the message
                    db.session.add(message)
                    generated_messages.append(generated_message)

                else:
                    # Update the message
                    message.content = generated_message
                    message.toxicity = toxicity
                    message.created = current_timestamp
        
        # Commit the changes
        db.session.commit()
    
    # Handle exceptions
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e.orig)}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "success", "message": "Data inserted successfully"}), 201

# Get all conversations
@bp.route('/get-conversations', methods=['GET'])
def get_conversations():

    from .models import db

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
