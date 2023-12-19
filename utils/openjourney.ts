import Replicate from "replicate";
const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

export default async function createPersonaWithOpenjourney(name: string, prompt: string): Promise<string> {
    try {
        console.log(`Calling OpenJourney to create image for name: ${name} and additionalPrompt: ${prompt}`);
        const response: any = await replicate.run(
            "prompthero/openjourney:ad59ca21177f9e217b9075e7300cf6e14f7e5b4505b87b9689dbd866e9768969",
            {
                input: {
                    prompt: `Photorealistic social media profile photo of a person called ${name} with the attributes ${prompt} - Sigma 24mm f/8 — wider angle, smaller focal length`,
                }
            }
        );

        if (response && typeof response[0] === 'string') {
            return response[0];
        } else {
            console.log(response);
            throw new Error('No image URL returned in OpenJourney response');
        }
    } catch (error) {
        console.error(`Error creating image with OpenJourney for name: ${name} and prompt: ${prompt}`, error);
        throw error;
    }
}
