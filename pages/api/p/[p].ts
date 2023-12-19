import type { NextApiRequest, NextApiResponse } from 'next';
import { connectToDatabase, addToCollection } from '../../../utils/mongo';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    try {
        // Connect to the database
        const { db } = await connectToDatabase();

        const exampleNewUser = {
            name: "Jane Doe",
            email: "jane.doe@example.com",
            age: 30,
            isActive: true
        };

        // Add the new user to the "users" collection
        await addToCollection(db, 'personas', exampleNewUser);

        // Fetch data from 'personas' collection
        const data = await db.collection('personas').find({}).toArray();

        // Send the response with the fetched data
        res.status(200).json(data);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: 'Unable to connect to the database or fetch data' });
    }
}
