import os
from flask import Blueprint, request, jsonify
from .services.openai_service import generate_character_motto
from .services.huggingface_service import toxicity_classification
from .utils import calculate_affinity, read_json
from flask import current_app
import glob


# Blueprint for API routes
bp = Blueprint("routes", __name__)

# Home route (displays "Welcome to my Flask app")
@bp.route("/", methods=["GET"])
def home_route():
    """
    Home endpoint to display a welcome message.
    """
    return "Welcome to my Flask app", 200

# Persona route
@bp.route('/personify', methods=['POST', 'GET'])
def generate_coordinates_route():

    """
    Endpoint to generate coordinates for persona scapes.

    This route processes a JSON input containing persona scapes and their respective coordinates. 
    It calculates the affinity of the provided coordinates to each predefined point in the specified
    persona scape, and returns the results.

    Methods
    -------
    POST/GET

    Returns
    -------
    JSON
        A JSON object containing the calculated affinities for each persona scape, or
        an error message if the input is invalid.

    Error Responses
    ---------------
    400 : Bad Request
        If the provided persona scape name is not found in the available compasses or
        if coordinates are not provided.
    """

    response_data = {}
    # Iterate over each persona scape in the input JSON.
    data = request.get_json()
    for persona_compass_key, persona_data in data.items():
        coordinates = persona_data.get('coordinates')
        persona_compass = persona_data.get('persona_scape', persona_compass_key) 

        
        # Create path to available_compasses json
        persona_path = os.path.join(current_app.root_path, "static", "persona_compasses")
        available_compasses = [f.split('.json')[0].split('/')[-1] for f in glob.glob(f"{persona_path}/*.json")]

        if persona_compass not in available_compasses:
            return jsonify({"error": f"'{persona_compass}' not found: Available scapes are: {available_compasses}"}), 400
        
        if not coordinates:
            return jsonify({"error": "Coordinates are required"}), 400
        
        file_path = os.path.join(current_app.root_path, "static", "persona_compasses", f"{persona_compass}.json")
        if not os.path.exists(file_path):
            return jsonify({"error": "Invalid 'compasses': Please check your input"}), 400
        
        # # Read in the json file
        persona_compass = read_json(file_path)
        # print(persona_scape)
        keyed_affinity = calculate_affinity(coordinates[0], coordinates[1], persona_compass)
        response_data[persona_compass_key] = keyed_affinity

    return jsonify({"response": response_data})

# OpenAI route
@bp.route('/generate-motto', methods=['POST', 'GET'])
def generate_character_motto_route():
    """
    Endpoint to generate a character motto based on a prompt and tone.

    This route processes a JSON input containing a prompt and a tone. It uses the
    OpenAI API to generate a motto and the Hugging Face API to classify the response
    for toxicity.

    Methods
    -------
    POST/GET

    Parameters
    ----------
    prompt : str
        The prompt to generate a motto from.
    motto_tone : str
        The tone of the motto to generate.

    Returns
    -------
    JSON
        A JSON object containing the generated motto, the toxicity classification
        of the motto, and the confidence of the classification.

    Error Responses
    ---------------
    400 : Bad Request
        If the prompt is not provided.
    """
    data = request.get_json()
    prompt = data.get('prompt')
    motto_tone = data.get('motto_tone')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Generate character motto
    response = generate_character_motto(prompt, motto_tone=motto_tone)

    # Classify the response for toxicity
    toxicity, confidence = toxicity_classification(response)

    return jsonify({"response": response, "toxicity": toxicity, "toxicity_confidence":confidence})
