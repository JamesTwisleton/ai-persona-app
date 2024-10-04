import OpenAI from 'openai';

/**
 * Generates a character motto using ChatGPT based on a given prompt and tone.
 * 
 * @param {string} prompt - The description of the character.
 * @param {string} mottoTone - The desired tone of the motto (e.g., 'neutral', 'sarcastic', 'comical', 'sombre').
 * @returns {Promise<string>} The generated motto.
 * @throws {Error} If there's an issue with the API call or response processing.
 */
export default async function chatWithChatGPT(prompt: string, mottoTone: string): Promise<string> {
    try {
        // Initialize the OpenAI client
        const openai = new OpenAI();

        // Construct the question for ChatGPT
        const question = `Generate a short character motto with the description: ${prompt} in a ${mottoTone} style`;
        console.log(`Calling ChatGPT with prompt: ${question}`);

        // Make the API call to ChatGPT
        const completion = await openai.chat.completions.create({
            model: 'gpt-4', // Using GPT-4 for better quality responses
            messages: [{ role: 'user', content: question }],
            max_tokens: 60, // Limit the response length to ensure a concise motto
            // TODO: @Dean can you explain this please?
            temperature: 0.7, // Adjust for creativity vs. consistency
        });

        // Extract the generated motto from the response
        const generatedResponse = completion.choices[0]?.message?.content?.trim();

        if (!generatedResponse) {
            throw new Error('No response generated from ChatGPT');
        }

        console.log(`ChatGPT motto response: ${generatedResponse}`);

        return generatedResponse;

    } catch (error) {
        console.error("Error in chatWithChatGPT:", error);
        throw error; // Re-throw to allow handling by the caller
    }
}
