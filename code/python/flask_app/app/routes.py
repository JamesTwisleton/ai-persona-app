# TODO: 

# DONE! load DB from database.db on app init. if database.db is empty, create initial tables in the style of post_archetype_attributes.

# DONE! Ensure database.db is persisted on app close/re-open

# DONE! refactor populate_database_with_initial_data to read from static directory

# DONE! initialize personas on app init (split out the persona creation from the init_conversations route)

# DONE! add "get-personas" route

# DONE! split logic in routes into separate files, so routes simply calls functions elsewhere

# DONE! Add UUIDs to personas and conversations

# DONE! fill out skeleton of "create-conversation" route using init-conversations as a basis

# DONE! create "get-conversation" endpoint to get created conversations by UUID

# get it working with frontend locally

# create docker-compose to run the frontend and backend together locally

# ensure database.db persistence is compatible with ECS

# add terraform to deploy to ECS and get it working online

from flask import Blueprint, Flask
from .functions.database import retrieve_personas, retrieve_conversations, retrieve_conversation
from .functions.conversations import generate_conversation

# Global variables
bp = Blueprint("routes", __name__)
app = Flask(__name__)

# Home route
@bp.route("/", methods=["GET"])
def home():
    return "ai-persona-app backend is alive!", 200

@bp.route('/api/backend/personas', methods=['GET'])
def get_personas():
    return retrieve_personas()

@bp.route('/api/backend/conversations/create', methods=['POST'])
def create_conversation():
    return generate_conversation()

@bp.route('/api/backend/conversation/<string:conversation_uuid>', methods=['GET'])
def get_conversation(conversation_uuid):
    return retrieve_conversation(conversation_uuid)

@bp.route('/api/backend/conversations', methods=['GET'])
def get_conversations():
    return retrieve_conversations()

# TODO: check the new logic mirrors this before removing
# # Route to initialize conversations objects
# @bp.route('/init-conversations', methods=['POST', 'GET'])
# def init_conversations():
#
#     from .models import db
#
#     current_timestamp = datetime.now().isoformat()
#     data = request.get_json()
#
#     if not data or 'conversations' not in data:
#         return jsonify({"error": "Invalid data"}), 400
#
#     try:
#         for conversation_data in data.get("conversations", []):
#             app.logger.info("Topic: ")
#             app.logger.info(conversation_data["topic"])
#
#             # Extract the user
#             user_data = conversation_data.get("user", {})
#
#             # Add the User
#             user = User.query.filter_by(id=user_data["id"]).first()
#             if not user:
#                 user = User(
#                     id=user_data["id"],
#                     uuid=str(uuid.uuid4())[:6],
#                     username=user_data["username"],
#                     creation_date=current_timestamp)
#                 db.session.add(user)
#
#             # Add the Conversation (based on user and conversation ID)
#             conversation = Conversation.query.filter_by(id=conversation_data["id"], user_id=user.id).first()
#             if not conversation:
#                 conversation = Conversation(
#                     id=conversation_data["id"],
#                     uuid=str(uuid.uuid4())[:6],
#                     topic=conversation_data["topic"],
#                     created=current_timestamp,
#                     user_id=user.id)
#                 db.session.add(conversation)
#             else:
#                 # Update conversation fields if necessary
#                 conversation.topic = conversation_data["topic"]
#                 conversation.created = current_timestamp
#
#             # Iterate through the Personas
#             generated_messages = []
#             for persona_data in conversation_data.get("personas", []):
#                 persona = Persona.query.filter_by(id=persona_data["id"]).first()
#
#                 if not persona:
#                     # Add the Persona
#                     persona = Persona(
#                         id=persona_data["id"],
#                         uuid=str(uuid.uuid4())[:6],
#                         user_id=user_data["id"],
#                         name=persona_data["name"],
#                         dob=persona_data["dob"],
#                         location=persona_data["location"],
#                         profile_picture_s3_bucket_address=persona_data["profile_picture_s3_bucket_address"],
#                         creation_date=current_timestamp)
#                     db.session.add(persona)
#
#                 # Add Attributes
#                 for attr_data in persona_data.get("attributes", []):
#
#                     # Grab the persona attributes
#                     persona_vector = {attr_data['name']: attr_data['value'] for attr_data in persona_data['attributes']}
#                     archetype_attributes = get_archetype_as_list(db)
#
#                     # Initialize the persona space and calculate cosine similarity
#                     persona_space = PersonaSpace(persona_vector, archetype_attributes)
#                     persona_affinities = persona_space.calculate_similarity()
#
#                     # Modify the pre-prompt based on the persona affinities
#                     pre_prompt = PRE_PROMPT
#                     pre_prompt['persona_affinities'] = persona_affinities
#
#                     # Check that the attribute type exists
#                     attribute_type_id = attr_data["attribute_type_id"]
#                     attribute = Attribute.query.filter_by(
#                         persona_id=persona.id, attribute_type_id=attribute_type_id
#                     ).first()
#
#                     if not attribute:
#                         # Add the Attribute
#                         attribute = Attribute(
#                             persona_id=persona.id,
#                             attribute_type_id=attribute_type_id,
#                             value=attr_data["value"])
#                         db.session.add(attribute)
#
#                 # Contact OPENAI to generate message
#                 generated_message = generate_character_motto(PRE_PROMPT, conversation_data["topic"])
#                 app.logger.info("Generated message")
#                 app.logger.info(generated_message)
#
#                 # Compute the message toxicity
#                 toxicity = toxicity_classification([generated_message])
#                 print(f"Message Toxicity: {toxicity}%", flush=True)
#
#                 # Check if the persona is already part of this conversation
#                 conversation_participant = ConversationParticipants.query.filter_by(
#                     conversation_id=conversation.id,
#                     persona_id=persona.id
#                 ).first()
#
#                 # If the persona is not already part of the conversation, add them
#                 if not conversation_participant:
#                     conversation_participant = ConversationParticipants(
#                         conversation_id=conversation.id,
#                         persona_id=persona.id,
#                         role="participant",
#                     )
#                     db.session.add(conversation_participant)
#
#                 # Assess message existence
#                 message = Message.query.filter_by(
#                     user_id=user.id,
#                     conversation_id=conversation.id,
#                     persona_id=persona.id).first()
#
#                 if not message:
#                     message = Message(
#                         persona_id=persona.id,
#                         uuid=str(uuid.uuid4())[:6],
#                         content=generated_message,
#                         toxicity=toxicity,
#                         created=current_timestamp,
#                         user_id=user.id,
#                         conversation_id=conversation.id)
#
#                     # Add the message
#                     db.session.add(message)
#                     generated_messages.append(generated_message)
#
#                 else:
#                     # Update the message
#                     message.content = generated_message
#                     message.toxicity = toxicity
#                     message.created = current_timestamp
#
#         # Commit the changes
#         db.session.commit()
#
#     # Handle exceptions
#     except IntegrityError as e:
#         db.session.rollback()
#         return jsonify({"status": "error", "message": str(e.orig)}), 400
#
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"status": "error", "message": str(e)}), 500
#
#     return jsonify({"status": "success", "message": "Data inserted successfully"}), 201
