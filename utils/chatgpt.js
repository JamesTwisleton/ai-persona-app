import { Configuration, OpenAIApi } from "openai";
const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY,
});

export default async function chatWithChatGPT(prompt, mottoTone) {
    try {
        const openai = new OpenAIApi(configuration);
        const questsion = `Generate a short character motto with the description: ${prompt} in a ${mottoTone} style`;
        console.log(`Calling ChatGPT with prompt: ${questsion}`);
        
        const response = await openai.createCompletion({
            model: "text-davinci-003",
            prompt: questsion,
          });

        const generatedText = response.data.choices[0].text;
        console.log("Generated Text:", generatedText);

        return generatedText;

    } catch (error) {
        console.error("Error:", error);
        throw error;
    }
}
