import OpenAI from 'openai/index.mjs';

export default async function createPersonaWithDalle(name: string, prompt: string) {
    try {
        const openai = new OpenAI();
        console.log(`Calling DALL-E to create image for name: ${name} and additionalPrompt: ${prompt}`);
        const response = await openai.images.generate({
        
            // TODO: this errors if this file is typescript? its apparently a supported field in the API?
            model: "dall-e-2",
            prompt: `Photorealistic social media profile photo of a person called ${name} with the attributes ${prompt} - Sigma 24mm f/8 — wider angle, smaller focal length`,
            n: 1,
            size: "256x256",
        });

        if (response.data && response.data[0] && response.data[0].url) {
            return response.data[0].url;
        } else {
            // Handle the case where the URL is not present in the response
            throw new Error('No image URL returned in the response');
        }
    } catch (error) {
        console.error(`Error creating image with DALL-E for name: ${name} and prompt: ${prompt}`, error);
        throw error; // or return a default string like 'Error' or a default image URL
    }
}
