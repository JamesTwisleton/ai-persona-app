import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase, getPersona } from '@lib/mongo';
import { fetchImagesForPersonaFromS3 } from '@/lib/aws';
import generateAndUploadPersona from "@/lib/generate-and-upload-persona";
import Persona from '@/models/Persona';

export async function POST(request: NextRequest) {
    const data = await request.json();
    const { name, model, prompt, mottoTone, force } = data;
    try {
        const { db } = await connectToDatabase();
        const existingPersona = await getPersona(db, name) as Persona;
        if (!existingPersona || (existingPersona && force)) {
            await generateAndUploadPersona(name, model, prompt, mottoTone);
            const newPersona = await getPersona(db, name) as Persona;
            return NextResponse.json(await fetchImagesForPersonaFromS3(newPersona));
        }

        console.log(`Force creation not selected, returning existing image(s) for ${name}`)
        return NextResponse.json(await fetchImagesForPersonaFromS3(existingPersona));
    } catch (e) {
        console.error('Error checking MongoDB for existing persona: ', e);
        return NextResponse.json({ error: 'Error checking MongoDB for existing persona' }, { status: 500 })
    }
}
