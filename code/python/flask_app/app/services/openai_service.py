import openai
from flask import current_app

def send_openai_prompt(prompt: str) -> str:
    openai.api_key = current_app.config['OPENAI_API_KEY']
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()

    except Exception as e:
        return f"Error: {str(e)}"
