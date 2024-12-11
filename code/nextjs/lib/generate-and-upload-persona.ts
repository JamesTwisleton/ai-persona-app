import { fetchAndUploadImage } from "./aws";
import chatWithChatGPT from "./chatgpt";
import createPersonaWithDalle from "./dall-e";
import { connectToDatabase, addPersonaOrUpdateImages } from "./mongo";
import createPersonaWithOpenjourney from "./openjourney";

/**
 * Generates a persona image, motto, and uploads the data to S3 and MongoDB.
 *
 * @param {string} name - The name of the persona.
 * @param {string} model - The AI model to use for image generation ("openjourney" or "dall-e").
 * @param {string} prompt - The prompt for generating the persona image.
 * @param {string} mottoTone - The desired tone for the persona's motto.
 */
export default async function generateAndUploadPersona(
  name: string,
  model: string,
  prompt: string,
  mottoTone: string,
) {
  // Validate and set the AI model to use
  let modelToUse: string = model as string;
  if (modelToUse !== "openjourney" && modelToUse !== "dall-e") {
    console.log(
      `Unsupported model provided: ${model}. Defaulting to 'openjourney'.`,
    );
    modelToUse = "openjourney";
  }

  // Generate the image URL using the selected AI model
  let imageUrl: string = "";
  switch (modelToUse) {
    case "openjourney":
      imageUrl = await createPersonaWithOpenjourney(name, prompt);
      break;
    case "dall-e":
      imageUrl = await createPersonaWithDalle(name, prompt);
      break;
  }

  // Generate a motto using ChatGPT
  const motto = await chatWithChatGPT(prompt, mottoTone);

  try {
    // Connect to the database
    const { db } = await connectToDatabase();

    // Fetch the generated image and upload it to S3
    const s3location = await fetchAndUploadImage(imageUrl, name, modelToUse);

    // Add or update the persona information in MongoDB
    await addPersonaOrUpdateImages(
      db,
      name,
      modelToUse,
      prompt,
      mottoTone,
      motto,
      imageUrl,
      s3location,
    );
  } catch (e) {
    console.error("Error uploading image to S3 and updating MongoDB:", e);
  }
}
