import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase, getPersona } from "@lib/mongo";
import { fetchImagesForPersonaFromS3 } from "@/lib/aws";
import generateAndUploadPersona from "@/lib/generate-and-upload-persona";
import Persona from "@/models/Persona";
import { capitalizeFirstLetter } from "@/lib/strings";

/**
 * Handles POST requests to create or retrieve a persona.
 * @param {NextRequest} request - The incoming request object.
 * @returns {Promise<NextResponse>} A JSON response with the persona data or an error message.
 */
export async function POST(request: NextRequest) {
  // Parse the request body
  const data = await request.json();
  const { name, model, prompt, mottoTone, force } = data;

  // Sanitize the name input
  const sanitisedName = capitalizeFirstLetter(name);

  try {
    // Connect to the database
    const { db } = await connectToDatabase();

    // Check if the persona already exists
    const existingPersona = (await getPersona(db, sanitisedName)) as Persona;

    // If the persona doesn't exist or force creation is requested
    if (!existingPersona || (existingPersona && force)) {
      // Generate and upload a new persona
      await generateAndUploadPersona(sanitisedName, model, prompt, mottoTone);

      // Fetch the newly created persona
      const newPersona = (await getPersona(db, sanitisedName)) as Persona;

      // Return the new persona's images
      return NextResponse.json(await fetchImagesForPersonaFromS3(newPersona));
    }

    // If the persona exists and force creation is not requested, get and return the existing persona
    console.log(
      `Force creation not selected, returning existing image(s) for ${sanitisedName}`,
    );
    return NextResponse.json(
      await fetchImagesForPersonaFromS3(existingPersona),
    );
  } catch (e) {
    // Log and return any errors
    console.error("Error checking MongoDB for existing persona: ", e);
    return NextResponse.json(
      { error: "Error checking MongoDB for existing persona" },
      { status: 500 },
    );
  }
}
