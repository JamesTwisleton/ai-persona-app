import OpenAI from 'openai';

/**
 * Creates a persona image using DALL-E based on the given name and prompt.
 *
 * @param {string} name - The name of the persona.
 * @param {string} prompt - Additional attributes or description for the persona.
 * @returns {Promise<string>} The URL of the generated image.
 * @throws {Error} If there's an issue with the API call or response processing.
 */
export default async function createPersonaWithDalle(
  name: string,
  prompt: string,
): Promise<string> {
  try {
    // Initialize the OpenAI client
    const openai = new OpenAI();

    console.log(
      `Calling DALL-E to create image for name: ${name} and additionalPrompt: ${prompt}`,
    );

    // Generate image using DALL-E
    const response = await openai.images.generate({
      // TODO: this errors if this file is typescript? its apparently a supported field in the API?
      model: 'dall-e-2', // Specify DALL-E 2 model
      prompt: `Photorealistic social media profile photo of a person called ${name} with the attributes ${prompt} - Sigma 24mm f/8 — wider angle, smaller focal length`,
      n: 1, // Generate one image
      size: '256x256', // Set image size
    });

    // Check if the response contains a valid image URL
    if (response.data && response.data[0] && response.data[0].url) {
      return response.data[0].url;
    } else {
      throw new Error('No image URL returned in the response');
    }
  } catch (error) {
    console.error(
      `Error creating image with DALL-E for name: ${name} and prompt: ${prompt}`,
      error,
    );
    throw error; // Re-throw the error for handling by the caller
  }
}
