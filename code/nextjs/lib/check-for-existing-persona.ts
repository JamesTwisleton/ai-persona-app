import Persona from "@/models/Persona";
import { connectToDatabase, getPersona } from "./mongo";
import { fetchImagesForPersonaFromS3 } from "./aws";

/**
 * Checks if a persona with the given name already exists in the database
 * and fetches its images if found.
 *
 * @param {string} name - The name of the persona to check for
 * @returns {Promise<PersonaDto | false>} A PersonaDto object if the persona exists, false otherwise
 */
export default async function checkForExistingPersona(name: string) {
  try {
    // Connect to the database
    const { db } = await connectToDatabase();

    // Attempt to retrieve the persona from the database
    const existingPersona = (await getPersona(db, name)) as Persona;

    if (existingPersona) {
      // If the persona exists, fetch its images from S3
      return await fetchImagesForPersonaFromS3(existingPersona);
    }

    // Return false if no matching persona is found
    return false;
  } catch (e) {
    // Log any errors that occur during the process
    console.error("Error checking MongoDB for existing persona: ", e);
    return false;
  }
}
