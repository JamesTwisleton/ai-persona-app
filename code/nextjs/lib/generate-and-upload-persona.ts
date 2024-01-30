import { fetchAndUploadImage } from "./aws";
import chatWithChatGPT from "./chatgpt";
import createPersonaWithDalle from "./dall-e";
import { connectToDatabase, addPersonaOrUpdateImages } from "./mongo";
import createPersonaWithOpenjourney from "./openjourney";

export default async function generateAndUploadPersona(name: string, model: string, prompt: string, mottoTone: string) {
    let modelToUse: string = model as string;
    if (modelToUse !== "openjourney" && modelToUse !== "dall-e") {
        console.log(`Unsupported model provided: ${model}. Defaulting to 'openjourney'.`);
        modelToUse = "openjourney";
    }

    // Call either model to get image url
    let imageUrl: string = "";
    switch (modelToUse) {
        case "openjourney":
            imageUrl = await createPersonaWithOpenjourney(name, prompt);
            break;
        case "dall-e":
            imageUrl = await createPersonaWithDalle(name, prompt);
            break;
    }

    // Generate a motto using chatGPT
    const motto = await chatWithChatGPT(prompt, mottoTone);

    // Fetch generated URL and save image to S3, put s3 location in mongo
    try {
        const { db } = await connectToDatabase();
        const s3location = await fetchAndUploadImage(imageUrl, name, modelToUse);
        await addPersonaOrUpdateImages(db, name, modelToUse, prompt, mottoTone, motto, imageUrl, s3location);
    } catch (e) {
        console.error('Error uploading image to S3 and putting in MongoDB:', e);
    }
}