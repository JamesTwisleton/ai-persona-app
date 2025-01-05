from openai import OpenAI
from dotenv import load_dotenv
from flask import current_app
import json
import os

# Load environment variables
load_dotenv()

def generate_response(pre_prompt, prompt):
    """
    Generate a response from OpenAI given a pre_prompt and a prompt
    
    :param pre_prompt: The pre-defined context to give the LLM, including the persona attributes
    :param prompt: The topic of discussion
    :return: The generated response as a string
    """
    # OpenAI API key setup
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

    try:
        # Combine pre_prompt and prompt
        question = f"{pre_prompt}\n{prompt}"

        # Make the API call to ChatGPT
        response = client.chat.completions.create(model="gpt-4",  # Using GPT-4 for better quality responses
        messages=[{"role": "user", "content": question}],
        max_tokens=60,  # Limit the response length to ensure a concise motto
        temperature=0.7)  # Adjust for creativity vs. consistency)

        # Extract and return the content of the response
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating motto: {e}"

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
