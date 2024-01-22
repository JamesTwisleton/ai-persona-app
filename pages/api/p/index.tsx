import type { NextApiRequest, NextApiResponse } from 'next';
import { connectToDatabase, addPersonaOrUpdateImages, getPersona } from '../../../utils/mongo';
import { fetchAndUploadImage, fetchImagesForPersonaFromS3 } from '@/utils/aws';
import createPersonaWithDalle from '@/utils/dall-e';
import chatWithChatGPT from '@/utils/chatgpt';
import createPersonaWithOpenjourney from '@/utils/openjourney';
import Persona from '@/models/Persona';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { name, model, prompt, mottoTone, motto, force } = req.body;
    try {
        const { db } = await connectToDatabase();
        const existingPersona = await getPersona(db, name) as Persona;
        if (!existingPersona || (existingPersona && force)) {
            await generateAndUploadPersona(name, model, prompt, mottoTone);
            const newPersona = await getPersona(db, name) as Persona;
            return res.status(200).json(await fetchImagesForPersonaFromS3(newPersona));
        }

        console.log(`Force creation not selected, returning existing image(s) for ${name}`)
        return res.status(200).json(await fetchImagesForPersonaFromS3(existingPersona));

        // await generateAndUploadPersona(name, model, prompt);
        // const newPersona = await getPersona(db, name) as Persona;
        // return res.status(200).json(await fetchImagesForPersonaFromS3(newPersona));

    } catch (e) {
        console.error('Error checking MongoDB for existing persona: ', e);
        return res.status(500).json({ error: 'Error checking MongoDB for existing persona' });
    }
}

async function generateAndUploadPersona(name: string, model: string, prompt: string, mottoTone: string) {
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