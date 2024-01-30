import Persona from "@/models/Persona";
import { connectToDatabase, getPersona } from "./mongo";
import { fetchImagesForPersonaFromS3 } from "./aws";

export default async function checkForExistingPersona(name: string) {
    try {
        const { db } = await connectToDatabase();
        const existingPersona = await getPersona(db, name) as Persona;
        if (existingPersona) {
            return await fetchImagesForPersonaFromS3(existingPersona);
        }
        return false;
    } catch (e) {
        console.error('Error checking MongoDB for existing persona: ', e);
        return false;
    }
}