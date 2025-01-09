from openai import OpenAI
from dotenv import load_dotenv
from flask import current_app
import json
import os

# Load environment variables
load_dotenv()

import json
from openai import OpenAI
from flask import current_app


def generate_response(pre_prompt, prompt):
    """
    Generate a response from OpenAI given a pre_prompt and a prompt.
    
    :param pre_prompt: The pre-defined context to give the LLM, including persona attributes (JSON object or string)
    :param prompt: The topic of discussion
    :return: The generated response as a string
    """
    # Ensure the pre_prompt is properly formatted as a string
    if isinstance(pre_prompt, dict):
        pre_prompt_content = json.dumps(pre_prompt, ensure_ascii=False, indent=None)
    elif isinstance(pre_prompt, str):
        try:
            # Validate the JSON structure if pre_prompt is a string
            pre_prompt_content = json.dumps(json.loads(pre_prompt), ensure_ascii=False, indent=None)
        except json.JSONDecodeError:
            return "Error: Invalid JSON format for pre_prompt."
    else:
        return "Error: pre_prompt must be a dictionary or JSON string."

    # OpenAI API key setup
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

    try:
        # Make the API call to ChatGPT
        message_payload = [{
            "role": "system", "content": pre_prompt_content},
            {"role": "user", "content": prompt}]
        
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for better quality responses
            messages=message_payload,
            max_tokens=500,  # Limit the response length
            temperature=0.7  # Adjust for creativity vs. consistency
        )

        # Return the generated response directly
        # print(message_payload, flush=True)
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating response: {e}"


# Example usage
if __name__ == "__main__":

    # Load pre-prompt from JSON file
    file_name = 'preprompt_v_0.1.json'
    with open(os.path.join(os.path.dirname(__file__), '..', 'static', 'preprompts', file_name)) as f:
        pre_prompt = json.load(f)

    # Modify the pre-prompt persona affinities
    new_affinities = {
        'economic': 0.7,
        'freedom': 0.5,
        'tone': 0.4,
        'culture': 0.8,
        'conflict': 0.6,
        'optimism': 0.9}

    # Update the pre-prompt
    pre_prompt['persona']['affinities'] = new_affinities

    # Example character description prompt
    prompt = "A wise, strategic leader with a focus on pragmatic solutions for global peace."

    # Generate the motto
    motto = generate_response(pre_prompt, prompt)
    print(f"Generated Motto: {motto}")
