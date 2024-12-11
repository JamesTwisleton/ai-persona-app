import Persona from '@/models/Persona';
import { MongoClient, Db } from 'mongodb';
import { ObjectId } from 'mongodb';

// MongoDB connection details
const uri = process.env.MONGODB_URI;
const dbName = process.env.MONGODB_DB;

// Ensure environment variables are set
if (!uri) {
  throw new Error('Please define the MONGODB_URI environment variable');
}

if (!dbName) {
  throw new Error('Please define the MONGODB_DB environment variable');
}

// Caching mechanism for MongoDB client and database connection
let cachedClient: MongoClient | null = null;
let cachedDb: Db | null = null;

/**
 * Establishes a connection to the MongoDB database.
 * @returns {Promise<{client: MongoClient, db: Db}>} The MongoDB client and database instance.
 */
export async function connectToDatabase() {
  if (cachedClient && cachedDb) {
    return { client: cachedClient, db: cachedDb };
  }

  const client = new MongoClient(uri!);

  await client.connect();

  const db = client.db(dbName!);

  // Cache the client and db for future use
  cachedClient = client;
  cachedDb = db;

  return { client, db };
}

/**
 * Adds a document to a specified collection in the database.
 * @param {Db} db - The database instance.
 * @param {string} collectionName - The name of the collection.
 * @param {Record<string, any>} document - The document to be inserted.
 */
export async function addToCollection(
  db: Db,
  collectionName: string,
  document: Record<string, any>,
) {
  const collection = db.collection(collectionName);
  await collection.insertOne(document);
}

/**
 * Adds a new persona or updates the images of an existing persona in the database.
 * @param {Db} db - The database instance.
 * @param {string} name - The name of the persona.
 * @param {string} model - The AI model used for image generation.
 * @param {string} additionalPrompt - Additional prompt used for image generation.
 * @param {string} mottoTone - The tone of the persona's motto.
 * @param {string} motto - The persona's motto.
 * @param {string} imageUrl - The URL of the generated image.
 * @param {string} s3location - The S3 location where the image is stored.
 */
export async function addPersonaOrUpdateImages(
  db: Db,
  name: string,
  model: string,
  additionalPrompt: string,
  mottoTone: string,
  motto: string,
  imageUrl: string,
  s3location: string,
) {
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
  const existingDoc = await collection.findOne({ name: name });

  if (existingDoc) {
    // Document exists, so update it
    console.log(`Found persona with name ${name} on mongo, updating images`);
    const persona = new Persona(
      existingDoc._id,
      existingDoc.name,
      existingDoc.images,
    );
    persona.addImage(image);
    await collection.updateOne(
      { _id: persona._id },
      { $set: { images: persona.images } },
    );
  } else {
    // Document does not exist, so create a new one
    console.log(
      `Didn't find persona with ${name} on mongo, creating new entry`,
    );
    const newPersona = new Persona(new ObjectId(), name, [image]);
    await collection.insertOne(newPersona);
  }
}

/**
 * Retrieves a persona from the database by name.
 * @param {Db} db - The database instance.
 * @param {string} name - The name of the persona to retrieve.
 * @returns {Promise<Persona | false>} The persona object if found, false otherwise.
 */
export async function getPersona(db: Db, name: string) {
  const collection = db.collection('personas');

  // Check if a document with the given name exists
  const existingDoc = await collection.findOne({ name: name });

  if (existingDoc) {
    console.log(`Found persona with name ${name} on mongo`);
    return new Persona(existingDoc._id, existingDoc.name, existingDoc.images);
  } else {
    console.log(`Didn't find persona with name ${name} on mongo`);
    return false;
  }
}
