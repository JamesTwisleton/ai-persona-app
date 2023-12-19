import { Configuration, OpenAIApi } from "openai";

const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY,
});

export default async function createPersonaWithDalle(name: string, prompt: string): Promise<string> {
    const openai = new OpenAIApi(configuration);

    try {
        console.log(`Calling DALL-E to create image for name: ${name} and additionalPrompt: ${prompt}`);
        const response = await openai.createImage({
            model: "dall-e-2",
            prompt: `Photorealistic social media profile photo of a person called ${name} with the attributes ${prompt} - Sigma 24mm f/8 — wider angle, smaller focal length`,
            n: 1,
            size: "256x256",
        });

        if (response.data && response.data.data && response.data.data.length > 0 && response.data.data[0].url) {
            return response.data.data[0].url;
        } else {
            // Handle the case where the URL is not present in the response
            throw new Error('No image URL returned in the response');
        }
    } catch (error) {
        console.error(`Error creating image with DALL-E for name: ${name} and prompt: ${prompt}`, error);
        throw error; // or return a default string like 'Error' or a default image URL
    }
}
