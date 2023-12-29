// import type { NextApiRequest, NextApiResponse } from 'next';
// import { connectToDatabase, addPersonaOrUpdateImages } from '../../../utils/mongo';
// import fetchAndUploadImage from '@/utils/aws';
// import createPersonaWithDalle from '@/utils/dall-e';
// import createPersonaWithOpenjourney from '@/utils/openjourney';
// import { prettifyUrlProvidedName } from '@/utils/strings';

// export default async function handler(req: NextApiRequest, res: NextApiResponse) {
//     const { p, prompt, model } = req.query;

//     let prettifiedName: string;
//     if (typeof p === 'string') {
//         prettifiedName = prettifyUrlProvidedName(p);
//     } else {
//         return res.status(400).json({ error: `Unable to parse provided name ${p}` });
//     }

//     let validatedPrompt: string
//     if (typeof prompt !== 'string') {
//         console.error('prompt is not a string');
//         validatedPrompt = "";
//     } else {
//         validatedPrompt = prompt;
//     }

//     let modelToUse: string = model as string;
//     if (modelToUse !== "openjourney" && modelToUse !== "dall-e") {
//         console.log(`Unsupported model provided: ${model}. Defaulting to 'openjourney'.`);
//         modelToUse = "openjourney";
//     }

//     // Call either model to get image url
//     let imageUrl: string = "";
//     switch (modelToUse) {
//         case "openjourney":
//             imageUrl = await createPersonaWithOpenjourney(prettifiedName, validatedPrompt);
//             break;
//         case "dall-e":
//             imageUrl = await createPersonaWithDalle(prettifiedName, validatedPrompt);
//             break;
//     }

//     // Fetch generated URL and save image to S3, put s3 location in mongo
//     try {
//         const { db } = await connectToDatabase();
//         const s3location = await fetchAndUploadImage(imageUrl, p, modelToUse);
//         addPersonaOrUpdateImages(db, prettifiedName, modelToUse, validatedPrompt, imageUrl, s3location);
//     } catch (e) {
//         console.error('Error uploading image to S3 and putting in MongoDB:', e);
//         return res.status(500).json({ error: 'Error uploading image to S3 and putting in MongoDB' });
//     }

//     // TODO: once persona is added to mongo (above), query mongo for the given name
//     // use the returned objects "images" array to query s3 and grab all the images for that name. 
//     // return the list of images and prompts.etc to the frontend to be displayed

//     // return image URL
//     return res.status(200).json({ "model": model, "image_url": imageUrl });
// }
