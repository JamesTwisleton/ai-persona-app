import { NextResponse } from "next/server";

const backend_url = process.env.BACKEND_URL;

export async function POST(req: Request) {
  try {
    const { topic, persona_uuids } = await req.json();

    // Validate environment variable
    if (!backend_url) {
      throw new Error("BACKEND_URL environment variable is not set.");
    }

    // Forward request to your backend’s create-conversation endpoint
    console.log(JSON.stringify({ topic, persona_uuids }));
    const response = await fetch(
      `${backend_url}/api/backend/conversations/create`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // The body includes topic + persona_uuids
        body: JSON.stringify({ topic, persona_uuids }),
      },
    );

    // If the backend request fails:
    if (!response.ok) {
      console.error("Failed to create conversation:", response.statusText);
      return NextResponse.json(
        { error: "Failed to create conversation" },
        { status: response.status },
      );
    }

    // Backend likely returns { "conversation_uuid": "...", ... }
    const data = await response.json();

    // Return the data to the frontend, so we can use conversation_uuid
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error creating conversation:", (error as Error).message);
    return NextResponse.json(
      { error: "An error occurred while creating conversation" },
      { status: 500 },
    );
  }
}
