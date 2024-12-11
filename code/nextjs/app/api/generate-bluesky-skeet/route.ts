import { NextRequest, NextResponse } from "next/server";
import { generateBlueskySkeet } from "@/lib/chatgpt";

/**
 * Handles requests to create bluesky skeet text via LLM
 * @param {NextRequest} request - The incoming request object.
 * @returns {Promise<NextResponse>} A JSON response with the bluesky skeet text from LLM
 */
export async function POST(request: NextRequest) {
  const data = await request.json();
  const { name, image } = data;

  const generatedPost = await generateBlueskySkeet(
    name,
    image.additional_prompt,
    image.motto,
  );

  return NextResponse.json({ generatedPost: generatedPost }, { status: 200 });
}
