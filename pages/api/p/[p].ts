import type { NextApiRequest, NextApiResponse } from 'next';
import { connectToDatabase, addToCollection } from '../../../utils/mongo';
import { prettifyUrlProvidedName } from '@/utils/strings';
import createPersonaWithDalle from '@/utils/dall-e';
import createPersonaWithOpenjourney from '@/utils/openjourney';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { p, prompt, model } = req.query;

    let prettifiedName: string;
    if (typeof p === 'string') {
        prettifiedName = prettifyUrlProvidedName(p);
    } else {
        // Handle the case where provided name p is not a string
        console.error('p is not a string');
        return res.status(400).json({ error: `Unable to parse provided name ${p}` });
    }

    // Check mongo for the provided name
    let data = null;
    try {
        const { db } = await connectToDatabase();

        // // Fetch data from 'personas' collection
        data = await db.collection('personas').find({ name: prettifiedName }).toArray();
    } catch (e) {
        console.error(e);
    }
    if (data != null && data.length > 0) {
        console.log("Found documents:", data);
        return res.status(200).json(data);
    }

    console.log(`No documents found with the name ${prettifiedName}`);

    // call either model and return
    let imageUrl: string;
    switch (model) {
        case "openjourney":
            // TODO: put prompt in post request
            imageUrl = await createPersonaWithOpenjourney(prettifiedName, prompt);
            res.redirect(imageUrl);
            // return res.status(200).json({"model":model, "image_url":imageUrl});
        case "dall-e":
            imageUrl = await createPersonaWithDalle(prettifiedName, prompt);
            res.redirect(imageUrl);
            // return res.status(200).json({"model":model, "image_url":imageUrl});
        default:
            throw new Error(`Unsupported model: ${model}`);
    }
    

    // // Add the new user to the "users" collection
    // await addToCollection(db, 'personas', exampleNewUser)

}
