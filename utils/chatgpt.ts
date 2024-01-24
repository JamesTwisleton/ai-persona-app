import OpenAI from 'openai';

export default async function chatWithChatGPT(prompt: string, mottoTone: string) {
    try {
        const openai = new OpenAI();

        const question = `Generate a short character motto with the description: ${prompt} in a ${mottoTone} style`;
        console.log(`Calling ChatGPT with prompt: ${question}`);

        const completion = await openai.chat.completions.create({
            model: 'gpt-4',
            messages: [{ role: 'user', content: question }],
        });
        const generatedResponse = completion.choices[0]?.message?.content;
        console.log(`ChatGPT motto response: ${generatedResponse}`);

        return generatedResponse as string;

    } catch (error) {
        console.error("Error:", error);
        throw error;
    }
}
