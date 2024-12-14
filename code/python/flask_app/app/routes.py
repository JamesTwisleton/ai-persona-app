from flask import Blueprint, request, jsonify
from .services.openai_service import send_openai_prompt

# Blueprint for API routes
bp = Blueprint("routes", __name__)

# Home route (displays "Welcome to my Flask app")
@bp.route("/", methods=["GET"])
def home_route():
    """
    Home endpoint to display a welcome message.
    """
    return "Welcome to my Flask app", 200

@bp.route('/send_openai_prompt', methods=['POST'])
def send_openai_prompt_route():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    response = send_openai_prompt(prompt)

    return jsonify({"response": response})
