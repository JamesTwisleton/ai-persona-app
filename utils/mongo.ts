import Persona from '@/models/Persona';
import { MongoClient, Db } from 'mongodb';
import { ObjectId } from "mongodb";
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

export async function addPersonaOrUpdateImages(db: Db, name: string, model: string,additionalPrompt: string, mottoTone: string, motto: string, imageUrl: string, s3location: string) {
    const collection = db.collection('personas');

    // Create the image object
    const image = {
        generated_image_url: imageUrl,
        s3_location: s3location,
        model: model,
        additional_prompt: additionalPrompt,
        mottoTone: mottoTone,
        motto: motto,
        upvotes: 1,
        downvotes: 0,
    };

    // Check if a document with the given name exists
    const existingDoc = await collection.findOne({ name: name});

    if (existingDoc) {
        // Document exists, so update it
        console.log(`Found persona with name ${name} on mongo, updating images`);
        const persona = new Persona(existingDoc._id, existingDoc.name, existingDoc.images);
        persona.addImage(image);
        await collection.updateOne(
            { _id: persona._id },
            { $set: { images: persona.images } }
        );
    } else {
        // Document does not exist, so create a new one
        console.log(`Didn't find persona with ${name} on mongo, creating new entry`);
        const newPersona = new Persona(new ObjectId(), name, [image]);
        await collection.insertOne(newPersona);
    }
}

export async function getPersona(db: Db, name: string) {
    const collection = db.collection('personas');

    // Check if a document with the given name exists
    const existingDoc = await collection.findOne({ name: name });

    if (existingDoc) {
        console.log(`Found persona with name ${name} on mongo`);
        return new Persona(existingDoc._id, existingDoc.name, existingDoc.images); // Document exists
    } else {
        console.log(`Didn't find persona with name ${name} on mongo`);
        return false; // Document does not exist
    }
}