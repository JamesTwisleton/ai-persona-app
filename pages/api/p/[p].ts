import type { NextApiRequest, NextApiResponse } from 'next';
import { connectToDatabase, addToCollection } from '../../../utils/mongo';
import { prettifyUrlProvidedName } from '@/utils/strings';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { p } = req.query;
    let prettifiedName: string;

    if (typeof p === 'string') {
        prettifiedName = prettifyUrlProvidedName(p);
    } else {
        // Handle the case where urlProvidedName is not a string
        // You might want to throw an error, set a default value, or handle it in another way
        console.error('p is not a string');
        prettifiedName = "";
    }

    try {
        // Connect to the database
        const { db } = await connectToDatabase();

        // Fetch data from 'personas' collection
        const data = await db.collection('personas').find({ name: prettifiedName }).toArray();

        if (data.length > 0) {
            console.log("Found documents:", data);
        } else {
            console.log(`No documents found with the name ${prettifiedName}`);
        }

        // // Add the new user to the "users" collection
        // await addToCollection(db, 'personas', exampleNewUser);

        // Send the response with the fetched data
        res.status(200).json(data);


    } catch (e) {
        console.error(e);
        res.status(500).json({ error: 'Unable to connect to the database or fetch data' });
    }
}
