import { NextRequest, NextResponse } from "next/server";
import { BskyAgent } from '@atproto/api'

/**
 * Handles POST requests to create or retrieve a persona.
 * @param {NextRequest} request - The incoming request object.
 * @returns {Promise<NextResponse>} A JSON response with the persona data or an error message.
 */
export async function POST(request: NextRequest) {

    if (!process.env.BLUESKY_USERNAME || !process.env.BLUESKY_PASSWORD || !process.env.BLUESKY_PROFILE_BASE_URL) {
        throw new Error("Necessary environment variables not set");
    }

    const data = await request.json();
    const { name, image, skeet } = data;

    // TODO: use the details in image for something?

    const agent = new BskyAgent({
        service: 'https://bsky.social'
    })
    await agent.login({
        identifier: process.env.BLUESKY_USERNAME,
        password: process.env.BLUESKY_PASSWORD
    });

    const postResponse = await agent.post({
        text: `Name: ${name}\nPost: ${skeet}`,
        createdAt: new Date().toISOString()
    });

    const postId = postResponse.uri.split('/').pop();

    const postUrl = `${process.env.BLUESKY_PROFILE_BASE_URL}${postId}`;

    return NextResponse.json({ blueskyUrl: postUrl }, { status: 200 });
}
