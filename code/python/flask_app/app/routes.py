# TODO: 

# DONE! load DB from database.db on app init. if database.db is empty, create initial tables in the style of post_archetype_attributes.

# DONE! Ensure database.db is persisted on app close/re-open

# DONE! refactor populate_database_with_initial_data to read from static directory

# DONE! initialize personas on app init (split out the persona creation from the init_conversations route)

# DONE! add "get-personas" route

# DONE! split logic in routes into separate files, so routes simply calls functions elsewhere

# Add UUIDs to personas and conversations

# fill out skeleton of "create-conversation" route using init-conversations as a basis

# create "get-conversation" endpoint to get created conversations by UUID

# get it working with frontend locally

# create docker-compose to run the frontend and backend together locally

# ensure database.db persistence is compatible with ECS

# add terraform to deploy to ECS and get it working online

import os
from datetime import datetime
import uuid
from flask import Blueprint, request, jsonify, Flask
from sqlalchemy.exc import IntegrityError
from .models import User, Persona, Attribute, Conversation, Message, ConversationParticipants
from .functions.openai import generate_character_motto
from .functions.huggingface import toxicity_classification
from .functions.database import retrieve_personas_from_database, retrieve_conversations_from_database
from .functions.utils import read_json, get_archetype_as_list, PersonaSpace
# Global variables
bp = Blueprint("routes", __name__)
PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'static', 'preprompts', 'preprompt_v_0.1.json')
PRE_PROMPT = read_json(PROMPT_PATH)
app = Flask(__name__)

# Home route
@bp.route("/", methods=["GET"])
def home_route():
    """
    Home endpoint to display a welcome message.
    """
    return "Welcome to my Flask app", 200

@bp.route('/personas', methods=['GET'])
def get_personas():
    return retrieve_personas_from_database()

@bp.route('/conversations', methods=['GET'])
def get_conversations():
    return retrieve_conversations_from_database()


@bp.route('/conversations/create', methods=['POST'])
def create_conversation():
    """
    Create a new conversation by providing a topic and a list of persona UUIDs.

    Expected JSON payload:
    {
        "topic": "Example Topic",
        "persona_uuids": ["abc123", "def456"],
    }
    """
    from .models import db

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    topic = data.get("topic")
    persona_uuids = data.get("persona_uuids")
    user_id = data.get("user_id")  # If you want to pass an explicit user

    if not topic or not persona_uuids:
        return jsonify({"error": "Missing required fields: 'topic' and 'persona_uuids'"}), 400

    try:
        current_timestamp = datetime.now().isoformat()

        # Create a new conversation with a generated short-UUID
        new_conversation = Conversation(
            user_id=0, # TODO: add user handling later
            uuid=str(uuid.uuid4())[:6], # TODO: maybe only truncate uuids in interactions with user?
            topic=topic,
            created=current_timestamp
        )
        db.session.add(new_conversation)

        # For each requested persona, retrieve from DB and generate messages
        generated_messages = []
        for persona_uuid in persona_uuids:
            persona = Persona.query.filter_by(uuid=persona_uuid).first()
            if not persona:
                app.logger.warning(f"No Persona found with UUID {persona_uuid}; skipping.")
                continue

            # Gather persona’s attributes from DB
            # Build the persona vector from the name/value pairs
            persona_vector = {
                attr.attribute_type_relation.name: attr.value
                for attr in persona.attributes_relation
            }

            # Retrieve the global archetype definitions
            archetype_attributes = get_archetype_as_list(db)

            # Calculate similarity/affinities
            persona_space = PersonaSpace(persona_vector, archetype_attributes)
            persona_affinities = persona_space.calculate_similarity()

            # Prepare the pre-prompt (copy or clone your static preprompt dict)
            pre_prompt = PRE_PROMPT.copy()
            pre_prompt["persona_affinities"] = persona_affinities

            # Generate the persona's message from OpenAI
            generated_text = generate_character_motto(pre_prompt, topic)

            # Compute toxicity
            toxicity = toxicity_classification([generated_text])
            app.logger.info(f"Message toxicity: {toxicity}")

            # Ensure persona is listed in conversation_participants
            conversation_participant = ConversationParticipants.query.filter_by(
                conversation_id=new_conversation.id,
                persona_id=persona.id
            ).first()
            if not conversation_participant:
                conversation_participant = ConversationParticipants(
                    conversation_id=new_conversation.id,
                    persona_id=persona.id,
                    role="participant",
                )
                db.session.add(conversation_participant)

            # Create new message for this persona in the conversation
            new_message = Message(
                persona_id=persona.id,
                user_id=0,
                conversation_id=new_conversation.id,
                uuid=str(uuid.uuid4())[:6],
                toxicity=toxicity,
                content=generated_text,
                created=current_timestamp
            )
            db.session.add(new_message)
            generated_messages.append(generated_text)

        db.session.commit()

        return jsonify({
            "status": "success",
            "conversation_uuid": new_conversation.uuid,
            "topic": new_conversation.topic,
            "generated_messages_count": len(generated_messages)
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

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
            app.logger.info("Topic: ")
            app.logger.info(conversation_data["topic"])

            # Extract the user
            user_data = conversation_data.get("user", {})

            # Add the User
            user = User.query.filter_by(id=user_data["id"]).first()
            if not user:
                user = User(
                    id=user_data["id"],
                    uuid=str(uuid.uuid4())[:6],
                    username=user_data["username"],
                    creation_date=current_timestamp)
                db.session.add(user)

            # Add the Conversation (based on user and conversation ID)
            conversation = Conversation.query.filter_by(id=conversation_data["id"], user_id=user.id).first()
            if not conversation:
                conversation = Conversation(
                    id=conversation_data["id"],
                    uuid=str(uuid.uuid4())[:6],
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
                        uuid=str(uuid.uuid4())[:6],
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
                    pre_prompt['persona_affinities'] = persona_affinities

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
                app.logger.info("Generated message")
                app.logger.info(generated_message)

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
                        uuid=str(uuid.uuid4())[:6],
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
