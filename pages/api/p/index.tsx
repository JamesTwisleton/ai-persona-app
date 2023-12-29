import type { NextApiRequest, NextApiResponse } from 'next';
import { connectToDatabase, addPersonaOrUpdateImages, getExistingPersona } from '../../../utils/mongo';
import {fetchAndUploadImage, fetchImagesForPersonaFromS3} from '@/utils/aws';
import createPersonaWithDalle from '@/utils/dall-e';
import createPersonaWithOpenjourney from '@/utils/openjourney';
import Persona from '@/models/Persona';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }
    const { name, model, prompt } = req.body;

    // if theres a mongo entry, go grab them and return them with a flag to say they already exist
    // so frontend can give option to force creating a new one
    try {
        const { db } = await connectToDatabase();
        const existingDoc = await getExistingPersona(db, name) as Persona;
        if (existingDoc) {
            return res.status(200).json(await fetchImagesForPersonaFromS3(existingDoc));
        }

        


    } catch (e) {
        console.error('Error checking MongoDB for existing persona: ', e);
        return res.status(500).json({ error: 'Error checking MongoDB for existing persona' });
    }



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

    // Fetch generated URL and save image to S3, put s3 location in mongo
    try {
        const { db } = await connectToDatabase();
        const s3location = await fetchAndUploadImage(imageUrl, name, modelToUse);
        addPersonaOrUpdateImages(db, name, modelToUse, prompt, imageUrl, s3location);
    } catch (e) {
        console.error('Error uploading image to S3 and putting in MongoDB:', e);
        return res.status(500).json({ error: 'Error uploading image to S3 and putting in MongoDB' });
    }

    // TODO: once persona is added to mongo (above), query mongo for the given name
    // use the returned objects "images" array to query s3 and grab all the images for that name. 
    // return the list of images and prompts.etc to the frontend to be displayed

    // return image URL
    return res.status(200).json({ "model": model, "image_url": imageUrl });
}
