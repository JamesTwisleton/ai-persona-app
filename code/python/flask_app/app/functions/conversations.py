import os
from ..models import db, Persona, Conversation, Message, ConversationParticipants
from flask import Flask, request, jsonify
from datetime import datetime
import uuid
from ..functions.utils import read_json, get_archetype_as_list, PersonaSpace
from ..functions.openai import generate_response
from ..functions.huggingface import toxicity_classification
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'preprompts', 'preprompt_v_0.3.json')
PRE_PROMPT = read_json(PROMPT_PATH)

def generate_conversation():
    """
    Create a new conversation by providing a topic and a list of persona UUIDs.

    Expected JSON payload:
    {
        "topic": "Example Topic",
        "persona_uuids": ["abc123", "def456"],
    }
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    topic = data.get("topic")
    persona_uuids = data.get("persona_uuids")

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
            generated_text = generate_response(pre_prompt, topic)
            app.logger.info(f"Generated message for {persona.name}: {generated_text}")

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
            "conversation_uuid": new_conversation.uuid,
            "topic": new_conversation.topic,
            "generated_messages_count": len(generated_messages)
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify ({"status": "error", "message": str(e)}), 500
