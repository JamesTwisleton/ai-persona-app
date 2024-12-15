import openai
from dotenv import load_dotenv
from flask import current_app

# def send_openai_prompt(prompt: str) -> str:
#     openai.api_key = current_app.config['OPENAI_API_KEY']
    
#     try:
#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=prompt,
#             max_tokens=150
#         )
#         return response.choices[0].text.strip()

#     except Exception as e:
#         return f"Error: {str(e)}"



def generate_character_motto(prompt, motto_tone):
    """
    Generate a short character motto based on the given description and tone.
    
    :param prompt: The description of the character
    :param motto_tone: The desired tone/style of the motto
    :return: The generated motto as a string
    """
    # openai.api_key 
    print(current_app.config['OPENAI_API_KEY'])

    try:
        # Construct the question for ChatGPT
        question = f"Generate a short character motto with the description: {prompt} in a {motto_tone} tone."
        print(f"Calling ChatGPT with prompt: {question}")

        # Make the API call to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Using GPT-4 for better quality responses
            messages=[{"role": "user", "content": question}],
            max_tokens=60,  # Limit the response length to ensure a concise motto
            temperature=0.7  # Adjust for creativity vs. consistency
        )
        
        # Extract and return the content of the response
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"Error generating motto: {e}"

# Example usage
if __name__ == "__main__":
    prompt = "brave knight who protects the weak"
    motto_tone = "heroic"
    motto = generate_character_motto(prompt, motto_tone)
    print(f"Generated Motto: {motto}")
