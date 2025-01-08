import { NextResponse } from "next/server";

const backend_url = process.env.BACKEND_URL;

export async function GET(
  request: Request,
  { params }: { params: { conversation_id: string } },
) {
  try {
    // Validate environment variable
    if (!backend_url) {
      throw new Error("BACKEND_URL environment variable is not set.");
    }

    const { conversation_id } = params;

    // Fetch the conversation from your backend
    const response = await fetch(
      `${backend_url}/api/backend/conversation/${conversation_id}`,
      {
        method: "GET",
      },
    );

    if (!response.ok) {
      console.error("Failed to fetch conversation:", response.statusText);
      return NextResponse.json(
        { error: "Failed to fetch conversation" },
        { status: response.status },
      );
    }

    // Return JSON response directly
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching conversation:", (error as Error).message);
    return NextResponse.json(
      { error: "An error occurred while fetching conversation" },
      { status: 500 },
    );
  }
}
