import { MongoClient, Db } from 'mongodb';

const uri = process.env.MONGODB_URI;
const dbName = process.env.MONGODB_DB;

if (!uri) {
    throw new Error('Please define the MONGODB_URI environment variable');
}

if (!dbName) {
    throw new Error('Please define the MONGODB_DB environment variable');
}

let cachedClient: MongoClient | null = null;
let cachedDb: Db | null = null;

export async function connectToDatabase() {
    if (cachedClient && cachedDb) {
        return { client: cachedClient, db: cachedDb };
    }

    const client = new MongoClient(uri!);

    await client.connect();

    const db = client.db(dbName!);

    cachedClient = client;
    cachedDb = db;

    return { client, db };
}

export async function addToCollection(db: Db, collectionName: string, document: Record<string, any>) {
    const collection = db.collection(collectionName);
    await collection.insertOne(document);
}

export async function addPersonaOrUpdateImages(db: Db, name: string, model: string, additionalPrompt: string, imageUrl: string, s3location: string) {
    const collection = db.collection('personas');

    // Create the image object
    const image = {
        image_url: imageUrl,
        s3_location: s3location,
        model: model,
        additional_prompt: additionalPrompt,
        upvotes: 1,
        downvotes: 0,
    };

    // Check if a document with the given name exists
    const existingDoc = await collection.findOne({ name: name });

    if (existingDoc) {
        // Document exists, so update it
        console.log(`Found persona with name ${name} on mongo, updating images`);
        await collection.updateOne(
            { name: name },
            { $push: { images: image } }
        );
    } else {
        // Document does not exist, so create a new one
        console.log(`Didn't find persona with ${name} on mongo, creating new entry`);
        await collection.insertOne({
            name: name,
            images: [image]
        });
    }
}
