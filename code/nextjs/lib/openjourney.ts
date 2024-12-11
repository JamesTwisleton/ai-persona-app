import Replicate from 'replicate';

// Initialize Replicate client with API token from environment variables
const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN,
});

/**
 * Creates a persona image using OpenJourney based on the given name and prompt.
 *
 * @param {string} name - The name of the persona.
 * @param {string} prompt - Additional attributes or description for the persona.
 * @returns {Promise<string>} The URL of the generated image.
 * @throws {Error} If there's an issue with the API call or response processing.
 */
export default async function createPersonaWithOpenjourney(
  name: string,
  prompt: string,
): Promise<string> {
  try {
    console.log(
      `Calling OpenJourney to create image for name: ${name} and additionalPrompt: ${prompt}`,
    );

    // Call the OpenJourney model using Replicate
    const response: any = await replicate.run(
      'prompthero/openjourney:ad59ca21177f9e217b9075e7300cf6e14f7e5b4505b87b9689dbd866e9768969',
      {
        input: {
          prompt: `Photorealistic social media profile photo of a person called ${name} with the attributes ${prompt} - Sigma 24mm f/8 — wider angle, smaller focal length`,
        },
      },
    );

    return response[0];

  } catch (error) {
    console.error(
      `Error creating image with OpenJourney for name: ${name} and prompt: ${prompt}`,
      error,
    );
    throw error; // Re-throw the error for handling by the caller
  }
}
