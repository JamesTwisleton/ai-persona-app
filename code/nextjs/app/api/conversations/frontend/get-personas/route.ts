import { NextResponse } from "next/server";

const backend_url = process.env.BACKEND_URL; // Fetch the backend URL from environment variables

export async function GET() {
  try {
    // Validate that BACKEND_URL is set
    if (!backend_url) {
      throw new Error("BACKEND_URL environment variable is not set.");
    }

    // Fetch personas from the backend API
    const response = await fetch(`${backend_url}/api/backend/personas`, {
      method: "GET",
      headers: {
        "Cache-Control": "no-store", // Prevent caching
      },
    });

    // Handle non-OK responses
    if (!response.ok) {
      console.error(
        "Failed to fetch personas from backend:",
        response.statusText,
      );
      return NextResponse.json(
        { error: "Failed to fetch personas from backend" },
        { status: response.status },
      );
    }

    // Parse the response body
    const data = await response.json();

    // Ensure the response contains the personas object
    if (!data.personas) {
      console.error("Invalid response format: Missing 'personas' object");
      return NextResponse.json(
        { error: "Invalid response format: Missing 'personas' object" },
        { status: 500 },
      );
    }

    // Return the personas object
    console.log(data.personas[0].attributes);
    return NextResponse.json(data.personas);
  } catch (error) {
    console.error("Error fetching personas:", (error as Error).message);
    return NextResponse.json(
      { error: "An error occurred while fetching personas" },
      { status: 500 },
    );
  }
}
