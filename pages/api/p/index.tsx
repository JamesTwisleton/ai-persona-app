import type { NextApiRequest, NextApiResponse } from 'next';
import { connectToDatabase, addPersonaOrUpdateImages, getPersona } from '../../../utils/mongo';
import { fetchAndUploadImage, fetchImagesForPersonaFromS3 } from '@/utils/aws';
import createPersonaWithDalle from '@/utils/dall-e';
import createPersonaWithOpenjourney from '@/utils/openjourney';
import Persona from '@/models/Persona';
import axios from 'axios'

// Get key from .env.local and create chatGPT request
// export const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
// async function sendToChatGPT(prompt: string): Promise<string> {
//     const apiKey = OPENAI_API_KEY;
  
//     const apiUrl = 'https://api.openai.com/v1/engines/davinci-codex/completions';
  
//     // TODO: Replace tone with user input
//     const tone = "sarcastic"
//     const personality_prompt = `Generate a short personal mottoTone based on the personality description: ${prompt}.
//                                 Do this in the tone of ${tone} `

//     try {
//       const response = await axios.post(
//         apiUrl,
//         {
//           prompt: personality_prompt,
//           max_tokens: 100,  // Adjust as necessary
//         },
//         {
//           headers: {
//             'Content-Type': 'application/json',
//             'Authorization': `Bearer ${apiKey}`,
//           },
//         }
//       );
  
//       const generatedText = response.data.choices[0].text;
//       return generatedText;
//     } catch (error) {
//       console.error('Error calling OpenAI API:', error);
//       return 'Error occurred while processing your request.';
//     }
//   }
  


export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { name, model, prompt, mottoTone, force } = req.body;
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

    // Fetch generated URL and save image to S3, put s3 location in mongo
    try {
        const { db } = await connectToDatabase();
        const s3location = await fetchAndUploadImage(imageUrl, name, modelToUse);
        await addPersonaOrUpdateImages(db, name, modelToUse, prompt, mottoTone, imageUrl, s3location);
    } catch (e) {
        console.error('Error uploading image to S3 and putting in MongoDB:', e);
    }
}